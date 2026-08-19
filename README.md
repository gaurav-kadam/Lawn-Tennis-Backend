# Tennis Backend

Same layered architecture as the Kusti backend (models -> repositories -> services -> routes),
same auth/security/JWT/logging, rebuilt for Lawn Tennis.

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env`, set your `DB_URL` (create a `tennis_db` database first)
3. `uvicorn app.main:app --reload`
4. Open `http://127.0.0.1:8000/docs`

## What's new vs Kusti
- **Domain rebuilt for tennis**: Tournament, Player, Official (kept, same shape) + a brand new
  **Match** module: `Match`, `MatchSet` (completed set history), `MatchPointLog` (point-by-point event log).
- **`app/services/tennis_engine.py`**: pure scoring engine mirroring the frontend's rules
  (0/15/30/40, deuce/advantage, tiebreak with 1-then-every-2 serve rotation, best-of-3/5).
  It's event-sourced: the match's live state is always computed by replaying the ordered
  point log, so **undo is just "delete last point log row, replay"** — no separate history
  tracking needed, and it can never drift out of sync.
- **Global exception handling** (`app/main.py`): every error — expected `HTTPException`s,
  Pydantic validation errors, database errors, or anything unhandled — is caught centrally
  and returned in one consistent JSON shape (`success`, `status_code`, `message`, `path`).
  Nothing internal (stack traces, SQL, file paths) leaks to the client; full details are
  still logged server-side via `app/utils/logger.py`.

## Key endpoints
- `POST /api/v1/auth/register`, `POST /api/v1/auth/login`
- `POST /api/v1/matches` — create a match (player names, format, first server)
- `POST /api/v1/matches/{id}/points` — record a point (`winner`, `point_type`, `remarks`)
- `POST /api/v1/matches/{id}/undo` — undo the last point
- `GET /api/v1/matches/{id}/scoreboard` — full live state + completed sets + display points
- `GET /api/v1/matches/{id}/logs` — full point-by-point history
- Standard CRUD (list/get/update/delete/restore) for `tournaments`, `players`, `officials`, `matches`

## Database migrations (Alembic)

Schema is managed by Alembic now — `create_all()` is not used.

**First-time setup:**
```bash
alembic upgrade head
```

**After changing a model** (e.g. adding a column to `Match`):
```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

**Always review the generated migration file in `alembic/versions/` before running upgrade** —
autogenerate is very good but not perfect (e.g. it won't detect a column rename on its own).

**Roll back one step** if something goes wrong:
```bash
alembic downgrade -1
```

## Exception handling (`app/exceptions/`)

Everything error-related lives in one place now:
- `custom_exceptions.py` — `NotFoundException` (404), `ConflictException` (409),
  `BadRequestException` (400), `UnauthorizedException` (401), `ForbiddenException` (403).
  Services raise these instead of raw `HTTPException(status_code=..., detail=...)`, so
  every "not found" etc. across the whole app uses the exact same status code.
- `handlers.py` — the 4 global handlers (`register_exception_handlers(app)` is called
  once from `main.py`). Catches `HTTPException`, validation errors, DB errors, and
  anything unhandled — one consistent JSON response shape, nothing internal leaks.
- `db_safety.py` — `safe_commit()` / `safe_delete()`, used by every repository so a
  failed DB write always rolls back the session before the error bubbles up.

## Role-based authorization

Three roles are seeded on startup: **Supervisor**, **Admin**, **Scorer**.

- **Supervisor** — full access to everything, always (matches the frontend's sidebar rule).
- **Admin** — manages tournaments, players, officials, and match records (create/edit/delete).
- **Scorer** — can view everything and record live points / undo during a match, but
  cannot create/delete tournaments, players, officials, or matches.
- User & role management (`/api/v1/users`, `/api/v1/roles`) is **Supervisor only**.

This is enforced with `require_roles(*roles)` in `app/middleware/auth_middleware.py`:
```python
current_user = Depends(require_roles("Admin"))          # Admin (or Supervisor)
current_user = Depends(require_roles("Admin", "Scorer")) # Admin or Scorer (or Supervisor)
current_user = Depends(require_roles())                  # Supervisor only
current_user = Depends(verify_token)                      # any logged-in user (read-only endpoints)
```

The role is embedded in the JWT at login (`role_name`), so authorization checks don't
need an extra database query. Note: if a user's role is changed, they need to log in
again for the new role to take effect (the old token still carries the old role until
it expires).

## Production hardening pass (latest update)

**Response format** (all errors now use one shape, replacing the earlier ad-hoc one):
```json
{"status": "error", "message": "...", "error": "NOT_FOUND", "path": "/api/v1/..."}
```

**Files changed:**
- `app/exceptions/custom_exceptions.py` — added `DatabaseException` (500, generic message).
- `app/exceptions/db_safety.py` — rewritten: raises `DatabaseException` (not raw
  `SQLAlchemyError`); added `commit: bool` param + a `transaction()` context manager so
  multi-write flows (recording a point = point-log insert + match state update + set-row
  sync) commit as **one atomic unit** instead of three independent commits.
- `app/exceptions/handlers.py` — new response shape; validation errors strip the raw
  `input` value (was echoing back submitted data, e.g. a mistyped password, in 422s);
  5xx vs 4xx now logged at different levels; added a last-resort `SQLAlchemyError`
  handler as defense-in-depth on top of `db_safety`.
- `app/utils/soft_delete.py` — now uses the same rollback + `DatabaseException` contract.
- `app/repositories/user_repo.py`, `match_repo.py` — use the shared `db_safety` helpers
  (removed duplicated inline `try/except`); `match_repo` write methods accept
  `commit=False` for the atomic-transaction flows above.
- `app/services/match_service.py` — `add_point()` / `undo_last_point()` now wrapped in
  `transaction()`; removed the unused `fastapi.HTTPException` import.
- `app/services/{tournament,player,official,user}_service.py` — removed unused
  `HTTPException`/`status` imports (already raised only custom exceptions).
- `app/schemas/user.py` — **split `UserCreate` (admin, trusted `role_id`) from
  `UserRegister` (public self-signup, no `role_id` field at all)** — fixes a real
  privilege-escalation bug where anyone could `POST /auth/register` with
  `role_id=1` and self-assign Supervisor. Public registration now always gets the
  least-privileged role ("Scorer"), enforced server-side in `UserService.register_user`.
- `app/schemas/{match,player,official}.py` — added `Literal` types (match_format,
  winner, point_type), length bounds, and a mobile-number pattern so bad input is
  rejected with 422 before it reaches a service.
- `app/core/security.py` — **switched from passlib's bcrypt wrapper to the `bcrypt`
  library directly.** passlib 1.7.x's self-test is incompatible with bcrypt ≥ 4.1 and
  raised `ValueError` on every hash/verify call — this broke register/login entirely.
  Same hash format (`$2b$...`), so no migration needed for existing hashes.
- `app/core/config.py` — startup validation: refuses to boot with a missing/placeholder
  `SECRET_KEY`, missing `DB_URL`, or (in production) missing `ALLOWED_ORIGINS`.
- `app/middleware/auth_middleware.py` — `verify_token` now rejects a validly-signed
  token that's missing `user_id`/`role_name` claims.
- `app/main.py` — `/docs`, `/redoc`, `/openapi.json` are disabled when `ENV=production`.

## Verification performed (all passing)

| # | Check | Result |
|---|---|---|
| 1 | Public `POST /users` without a token | 401 |
| 2 | `POST /auth/register` with `role_id` in payload | ignored — account created as Scorer |
| 3 | Login with wrong password | 401, generic message |
| 4 | Valid login | 200, JWT contains `role_name` |
| 5 | Protected route, no token | 401 |
| 6 | Protected route, garbage token | 401 |
| 7 | Scorer calling an Admin-only route | 403 `FORBIDDEN` |
| 8 | Scorer reading a GET route | 200 |
| 9 | GET on a missing resource | 404 `NOT_FOUND` |
| 10 | Duplicate registration | 409 `CONFLICT` |
| 11 | Short password | 422 with field-level detail, no echoed password |
| 12 | Supervisor on an Admin-only route | 200 (bypass confirmed) |
| 13 | Supervisor on the Supervisor-only `/users` route | 200 |
| 14 | Full scoring flow: 4 points → 1 game won, score reset to 0-0 | correct |
| 15 | Undo last point → state reverts exactly (3 pts, 0 games) | correct |
| 16 | Forced DB unique-constraint violation | `DatabaseException` (500, generic), session rolled back, row count unaffected, full SQL error only in server log |

All done against a real running instance (`uvicorn` + SQLite via Alembic), not just
unit-level checks.

## Known non-issues (reviewed, no action needed)

- **IDOR**: tournaments/players/officials/matches are shared organizational resources,
  not per-user private data — any authenticated user being able to read any record by ID
  is the intended design (same as the reference architecture), not an authorization gap.
- **File uploads / path traversal**: no file-upload endpoints exist in this backend, so
  there's no surface for this class of issue.
- **SQL injection**: 100% SQLAlchemy ORM (`db.query(...)`, `.filter(...)`) throughout —
  no raw/string-concatenated SQL anywhere in the project.

## Remaining items (not done — out of scope for this pass, listed for visibility)

- Rate limiting on `/auth/login` (brute-force protection) — proposed earlier, not yet implemented.
- Refresh tokens / token revocation (current JWTs are stateless and can't be invalidated
  before they expire — acceptable for now given the short 60-minute expiry, but worth
  revisiting if longer sessions are needed).
- Structured request-ID tracing through logs.

## Exception architecture updated to match reference pattern

`app/exceptions/` now follows the exact reference structure:
- `base.py` — `AppException(Exception)`, a plain exception (not an `HTTPException`
  subclass): `message`, `status_code`, `details`.
- `custom_exceptions.py` — `NotFoundException` (404), `ConflictException` (409),
  `BadRequestException` (400), `AuthenticationException` (401),
  `AuthorizationException` (403), `DatabaseException` (500),
  `InternalServerException` (500).
- `handlers.py` — `app_exception_handler` (all `AppException`s),
  `validation_exception_handler` (422, field-level errors, no echoed input),
  `http_exception_handler` (plain `HTTPException`, e.g. HTTPBearer's own
  "Not authenticated"), `global_exception_handler` (last-resort 500).
  `register_exception_handlers(app)` wires all four via `app.add_exception_handler`.

**Response shape** (every error, everywhere):
```json
{"success": false, "status": 404, "message": "Tournament not found", "data": null, "details": null}
```

Services/repositories/middleware now raise `NotFoundException`, `ConflictException`,
`BadRequestException`, `AuthenticationException`, `AuthorizationException`, or
`DatabaseException` directly - no more raw `HTTPException` anywhere in business logic.
Re-verified end-to-end after the change (register, duplicate/409, missing token/401,
short password/422, missing resource/404, role violation/403) - all producing the
exact shape above.

## Doubles match support (latest update)

Added Doubles alongside existing Singles, with minimal, backward-compatible changes.

**Files changed:**
- `app/models/match.py` — added `match_type` (SINGLES/DOUBLES), `player3_id/name`,
  `player4_id/name`, `service_order` (JSON list). Added a **computed, non-DB**
  `current_server` property: Singles returns the existing `server` field unchanged;
  Doubles derives the individual server from `service_order`, rotating one step per
  completed game (`total_completed_games % len(service_order)`), computed purely from
  persisted set/game counts. **The scoring engine (`tennis_engine.py`) was not touched
  at all** — it still only knows two sides (PLAYER1/PLAYER2 = team1/team2 for Doubles).
- `app/schemas/match.py` — added `MatchType`, `IndividualPlayerSlot` (service_order
  only); `PlayerSlot` (scoring winner) stays `PLAYER1`/`PLAYER2` only, so the points
  API is unchanged. `MatchCreate`/`MatchUpdate` validate: Doubles needs player3/4 +
  exactly 4 unique service_order entries covering PLAYER1-4; Singles must have an
  empty service_order. `MatchResponse` exposes all new fields + `current_server`.
- `app/services/match_service.py` — Doubles create maps `service_order[0]` to the
  correct engine team side (PLAYER1/PLAYER2→team1, PLAYER3/PLAYER4→team2);
  `update_match` rejects doubles-metadata edits on a Singles match.
- `alembic/versions/2a6b7718a2a6_add_doubles_match_support.py` — new migration
  (`down_revision = 158e782f7c3c`, does not touch the original migration). All new
  columns nullable or `server_default`d, using `batch_alter_table` for MySQL/SQLite
  portability. Existing Singles rows behave as `match_type='SINGLES'`,
  `service_order=[]`, `player3/4=NULL` automatically.

**No changes to:** `tennis_engine.py`, routers, auth/exception architecture, repositories
(beyond the model's new columns being pass-through), Singles points/undo/scoreboard endpoints.

**Verified (real server, SQLite via Alembic, migrating from the pre-existing base
schema exactly like a production upgrade):**
- Singles create/GET/scoring/undo all unchanged (`current_server` mirrors `server`).
- Doubles create with valid 4-player service_order → 200, `current_server == service_order[0]`.
- After 1 completed game → server rotates to `service_order[1]`; after 2 games →
  `service_order[2]`; undo of the winning point correctly reverts the rotation.
- Rejected: DOUBLES with 3-entry service_order, DOUBLES missing `player3_name`,
  SINGLES with a non-empty service_order — all 422 with field-level detail.
- `GET /matches` (list) and `GET /matches/{id}/scoreboard` both include full Doubles metadata.
- `alembic upgrade head` applied cleanly on top of the original base migration.
