from databases import Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models.material import Base

DATABASE_URL = "sqlite:///./test.db"  # Use your preferred database URL

# Connect to the database
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
