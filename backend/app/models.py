import enum

from sqlalchemy import Boolean, Column, Enum, Integer, String

from .database import Base


class UserRole(str, enum.Enum):
    PROFESIONAL_SALUD = "PROFESIONAL_SALUD"
    ADMINISTRADOR = "ADMINISTRADOR"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
