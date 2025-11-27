from models import Candidate, Keyword, User
from sqlmodel import Session, select
from icecream import ic
from DB.create_database import engine


def main():
    search_term = "оптимізація"
    search_pattern = f"%{search_term}%"

    with Session(engine) as s:
        statement = select(Keyword).where(Keyword.word.like(search_pattern))
        res = s.exec(statement).all()
        kw = set(kword.word for kword in res)
        ic(kw, len(kw))


def show_users():
    with Session(engine) as s:
        statement = select(User)
        res = s.exec(statement).all()

        ic(res)


if __name__ == '__main__':
    main()
    show_users()
