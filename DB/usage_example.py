from models import Candidate, engine, Keyword
from sqlmodel import Session, select
from icecream import ic


def main():
    search_term = "оптимізація"
    search_pattern = f"%{search_term}%"

    with Session(engine) as s:
        statement = select(Keyword).where(Keyword.word.like(search_pattern))
        res = s.exec(statement).all()
        kw = set(kword.word for kword in res)
        ic(kw, len(kw))


if __name__ == '__main__':
    main()
