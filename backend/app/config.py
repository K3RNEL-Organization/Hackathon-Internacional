import os

JWT_SECRET = os.getenv("RISA_JWT_SECRET", "risa-data-dev-secret-change-me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

DATABASE_URL = os.getenv("RISA_DATABASE_URL", "sqlite:///./risa_data.db")

CORS_ORIGINS = os.getenv("RISA_CORS_ORIGINS", "http://localhost:3000").split(",")
