from sqlmodel import SQLModel, Field, create_engine, Relationship
from typing import Optional, List
from sqlalchemy import UniqueConstraint

engine = create_engine("sqlite:///defense.db", echo=False, future=True)


class Institution(SQLModel, table=True):
    edrpou: str = Field(primary_key=True)
    name: str = Field(index=True)

    candidates: List["Candidate"] = Relationship(back_populates="institution")


class Specialty(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    name: str

    candidates: List["Candidate"] = Relationship(back_populates="specialty")


class CandidateKeyword(SQLModel, table=True):
    candidate_orcid: str = Field(
        foreign_key="candidate.orcid", primary_key=True
    )
    keyword_id: int = Field(
        foreign_key="keyword.id", primary_key=True
    )

    __table_args__ = (
        UniqueConstraint("candidate_orcid", "keyword_id"),
    )


class Keyword(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    word: str = Field(unique=True, index=True)

    candidates: List["Candidate"] = Relationship(
        back_populates="keywords",
        link_model=CandidateKeyword
    )


class Candidate(SQLModel, table=True):
    orcid: str = Field(primary_key=True)
    name: str
    faculty: Optional[str] = None
    hei_edrpou: str = Field(foreign_key="institution.edrpou")
    degree_spec_id: int = Field(foreign_key="specialty.id")

    institution: Optional[Institution] = Relationship(back_populates="candidates")
    specialty: Optional[Specialty] = Relationship(back_populates="candidates")
    keywords: List[Keyword] = Relationship(
        back_populates="candidates",
        link_model=CandidateKeyword
    )


def create_db():
    SQLModel.metadata.create_all(engine)
    print("created")


if __name__ == "__main__":
    create_db()
