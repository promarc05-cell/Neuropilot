from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# SQLite database file
DATABASE_URL = "sqlite:///./neuro_pilot.db"


# Create the database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for database models
Base = declarative_base()


# Dependency used by FastAPI routes later
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()