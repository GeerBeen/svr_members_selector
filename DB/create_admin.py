from sqlmodel import Session, select
from models import User
from DB.auth import hash_password
from DB.create_database import engine


def create_admin():
    with Session(engine) as session:
        admin = User(
            username="admin",
            hashed_password=hash_password("admin"),
            is_admin=True
        )
        session.add(admin)
        session.commit()
        print("Адмін створений!")


def create_admin_on_start():
    with Session(engine) as session:
        statement = select(User).where(User.username == "admin")
        admin = session.exec(statement)
        if not admin:
            create_admin()


if __name__ == '__main__':
    create_admin()
