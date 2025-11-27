from sqlmodel import create_engine, SQLModel, Session
from DB.create_admin import create_admin
engine = create_engine("sqlite:///defense.db", echo=False)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("База створена або вже існує")


if __name__ == "__main__":
    create_admin()
    create_db_and_tables()

