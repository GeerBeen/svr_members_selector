# DB/database.py
from sqlmodel import create_engine, SQLModel
from pathlib import Path

# Корінь проєкту — завжди однаковий
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "defense.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)