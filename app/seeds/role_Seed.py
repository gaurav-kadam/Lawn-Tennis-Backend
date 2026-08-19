from sqlalchemy.orm import Session
from app.models.role import Role


def seed_roles(db: Session):
    roles = ["Supervisor", "Scorer", "Admin"]

    for role_name in roles:
        exists = db.query(Role).filter(Role.role_name == role_name).first()
        if not exists:
            db.add(Role(role_name=role_name, is_active=True))

    db.commit()
