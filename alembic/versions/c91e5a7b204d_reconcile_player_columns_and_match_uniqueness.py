"""Reconcile player columns and match record uniqueness.

Revision ID: c91e5a7b204d
Revises: b7f1c2d9e4a6

Partially reversible: player columns are intentionally retained on downgrade
because ownership cannot be inferred from current schema state.

The two exact unique names are reserved for this correction. Upgrade accepts
an already-correct named index (including a partial previous attempt); downgrade
removes it under that explicit policy, not an inferred creation history.

Run online with a single migration operator and application writes quiesced.
MySQL DDL is not transactionally reversible across these operations. On failure,
inspect the schema before retrying; do not assume earlier DDL was rolled back.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "c91e5a7b204d"
down_revision = "b7f1c2d9e4a6"
branch_labels = None
depends_on = None

_TARGETS = (
    ("match_events", "event_number", "uq_match_events_match_id_event_number"),
    ("match_sets", "set_number", "uq_match_sets_match_id_set_number"),
)


def _abort(errors):
    if errors:
        raise RuntimeError("Corrective migration preflight failed:\n- " + "\n- ".join(errors))


def _inspector(expected_revision):
    if op.get_context().as_sql:
        raise RuntimeError("This corrective migration requires an online MySQL connection.")
    bind = op.get_bind()
    if bind.dialect.name != "mysql":
        raise RuntimeError("This corrective migration supports MySQL only.")
    inspector = sa.inspect(bind)
    if not inspector.has_table("alembic_version"):
        raise RuntimeError("Missing alembic_version; no DDL performed.")
    revisions = list(bind.execute(sa.text("SELECT version_num FROM alembic_version")).scalars())
    if revisions != [expected_revision]:
        raise RuntimeError(
            f"Expected only Alembic revision {expected_revision}; found {revisions!r}."
        )
    return bind, inspector


def _player_columns(inspector, errors):
    if not inspector.has_table("players"):
        errors.append("Required table players is missing.")
        return []
    columns = {c["name"]: c for c in inspector.get_columns("players")}
    missing = []
    for name in ("weight", "category"):
        column = columns.get(name)
        if column is None:
            missing.append(name)
            continue
        kind = column["type"]
        if name == "weight":
            compatible = (
                isinstance(kind, mysql.FLOAT)
                and kind.precision in (None, 24)
                and kind.scale is None
                and not kind.unsigned
                and not kind.zerofill
            )
        else:
            compatible = isinstance(kind, mysql.VARCHAR) and kind.length == 50
        if (
            not compatible
            or column["nullable"] is not True
            or column.get("default") is not None
            or column.get("computed")
        ):
            errors.append(
                f"players.{name} must be compatible with "
                f"{'FLOAT' if name == 'weight' else 'VARCHAR(50)'} NULL without "
                "a non-NULL default or generated expression; existing column will not be altered."
            )
    return missing


def _target(bind, inspector, table, number, name, errors, downgrade=False):
    if not inspector.has_table(table):
        errors.append(f"Required table {table} is missing.")
        return False
    columns = {c["name"]: c for c in inspector.get_columns(table)}
    wanted = ["match_id", number]
    valid_columns = all(
        c in columns
        and isinstance(columns[c]["type"], sa.Integer)
        and columns[c]["nullable"] is False
        for c in wanted
    )
    if not valid_columns:
        errors.append(f"{table} requires non-null integer columns {wanted}.")

    fks = inspector.get_foreign_keys(table)
    expected_fk = [
        fk for fk in fks
        if fk["constrained_columns"] == ["match_id"]
        and fk["referred_table"] == "matches"
        and fk["referred_columns"] == ["id"]
        and fk.get("referred_schema") in (None, inspector.default_schema_name)
    ]
    if len(expected_fk) != 1:
        errors.append(f"{table}.match_id must reference matches.id exactly once.")
    elif any(
        str(expected_fk[0].get("options", {}).get(action) or "NO ACTION").upper()
        not in ("NO ACTION", "RESTRICT")
        for action in ("ondelete", "onupdate")
    ):
        errors.append(f"{table}.match_id has unexpected FK actions; no FK will be altered.")

    indexes = inspector.get_indexes(table)
    uniques = inspector.get_unique_constraints(table)
    # MySQL reflects a unique constraint as both a constraint and an index.
    objects = indexes + [dict(u, unique=True) for u in uniques]
    pk = inspector.get_pk_constraint(table)
    if pk.get("name") == name or any(fk.get("name") == name for fk in fks):
        errors.append(f"{table}.{name} conflicts with a non-unique-constraint object.")

    exact = [obj for obj in objects if obj["name"] == name]
    correct = bool(exact) and all(
        obj.get("unique")
        and obj.get("column_names") == wanted
        and not obj.get("dialect_options", {}).get("mysql_length")
        and str(obj.get("type", "BTREE")).upper() == "BTREE"
        for obj in exact
    )
    if exact and not correct:
        errors.append(f"{table}.{name} exists but is not the expected full-column unique index.")
    if downgrade and not exact:
        errors.append(f"Expected owned constraint {table}.{name} is missing.")

    for obj in objects:
        if (
            obj["name"] != name
            and obj.get("unique")
            and len(obj.get("column_names") or []) == 2
            and set(obj["column_names"]) == set(wanted)
        ):
            errors.append(f"{table} has equivalent uniqueness under unexpected name {obj['name']}.")
    if len(pk.get("constrained_columns") or []) == 2 and set(pk["constrained_columns"]) == set(wanted):
        errors.append(f"{table} already enforces this uniqueness through its primary key.")

    if not downgrade and valid_columns:
        # Identifiers come only from the fixed _TARGETS above.
        duplicate = bind.execute(sa.text(
            f"SELECT 1 FROM `{table}` GROUP BY match_id, `{number}` "
            "HAVING COUNT(*) > 1 LIMIT 1"
        )).first()
        if duplicate:
            errors.append(f"{table} contains duplicate (match_id, {number}) groups.")

    if downgrade:
        supporting = [
            index for index in indexes
            if index["name"] != name
            and (index.get("column_names") or [])[:1] == ["match_id"]
            and not index.get("dialect_options", {}).get("mysql_length")
            and str(index.get("type", "BTREE")).upper() == "BTREE"
        ]
        if not supporting and (pk.get("constrained_columns") or [])[:1] != ["match_id"]:
            errors.append(
                f"Cannot remove {table}.{name}: no other match_id-leading FK index. "
                "Restore an approved supporting index separately before downgrade."
            )
    return correct


def upgrade():
    bind, inspector = _inspector(down_revision)
    errors = []
    missing = _player_columns(inspector, errors)
    existing = [
        _target(bind, inspector, table, number, name, errors)
        for table, number, name in _TARGETS
    ]
    # All tables are checked before the first DDL statement.
    _abort(errors)
    if "weight" in missing:
        op.add_column("players", sa.Column("weight", sa.Float(), nullable=True))
    if "category" in missing:
        op.add_column("players", sa.Column("category", sa.String(50), nullable=True))
    for (table, number, name), present in zip(_TARGETS, existing):
        if not present:
            op.create_unique_constraint(name, table, ["match_id", number])


def downgrade():
    bind, inspector = _inspector(revision)
    errors = []
    for table, number, name in _TARGETS:
        _target(bind, inspector, table, number, name, errors, downgrade=True)
    # Check BOTH constraints and supporting indexes before dropping either.
    _abort(errors)
    for table, _, name in reversed(_TARGETS):
        op.drop_constraint(name, table, type_="unique")
    # Never drop weight/category: they may predate this migration.
