from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import User, UserRole
from .security import hash_password

SEED_USERS = [
    {
        "email": "profesional@risadata.com",
        "password": "Profesional#2026",
        "full_name": "Dra. Valentina Rios",
        "role": UserRole.PROFESIONAL_SALUD,
    },
    {
        "email": "admin@risadata.com",
        "password": "Admin#2026",
        "full_name": "Administrador RISA",
        "role": UserRole.ADMINISTRADOR,
    },
]


def seed_users(db: Session) -> None:
    for seed in SEED_USERS:
        exists = db.query(User).filter(User.email == seed["email"]).first()
        if exists:
            continue
        db.add(
            User(
                email=seed["email"],
                hashed_password=hash_password(seed["password"]),
                full_name=seed["full_name"],
                role=seed["role"],
                is_active=True,
            )
        )
    db.commit()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()
