from sqlmodel import Session, select
from DB import models
from . import profile

# конвертує models.Candidate в profile.Profile
def to_profile(cand: models.Candidate):
    if cand is None:
        return None
    
    keyword_list = [kw.word for kw in cand.keywords]

    return profile.Profile(
        orcid=cand.orcid,
        specialty_id=cand.degree_spec_id,
        keywords=keyword_list
    )

# повертає вагу ключового слова
def weight(keyword):
    return 1


# повертає кандидата з вказаним orcid
def get_cand(cand_id):
    with Session(models.engine) as session:
        
        statement = select(models.Candidate).where(models.Candidate.orcid == cand_id)
        cand = session.exec(statement).first()
        
        if cand is None:
            return None
        
        return to_profile(cand)


# повертає заявку
# ЗАГЛУШКА
def get_app():
    return get_cand("0000-0002-1665-0361")


# повертає усіх кандидатів
def get_all_cands():
    cands = set()

    with Session(models.engine) as session:
        statement = select(models.Candidate)
        candidate_db = session.exec(statement).all()

        for candidate in candidate_db:
            # Використовуємо приватний конвертер
            new_cand = to_profile(candidate) 
            if new_cand:
                cands.add(new_cand)

        return cands


# повертає усіх кандидатів з заданою спеціальністю
def get_cands_by_specialty(specialty_id):
    cands = set()

    with Session(models.engine) as session:
        # отримання кандлидатів із заданим specialty_id
        candidate_statement = select(models.Candidate).where(
            models.Candidate.degree_spec_id == specialty_id
        )
        candidate_db = session.exec(candidate_statement).all()

        for cand in candidate_db:
            new_cand = to_profile(cand)
            if new_cand:
                cands.add(new_cand)

        return cands


# повертає суміжні до переданої в якості аргументу спеціальності, 
# включно з самою спеціальністю
def get_spec_range(specialty_id):
    return set([specialty_id])


# повертає усіх кандидатів з заданого відрізку спеціальностей
def get_cands_by_spec_range(specialty_id):
    cands = set()

    spec_range = get_spec_range(specialty_id)
    for spec in spec_range:
        cands.update( get_cands_by_specialty(spec) )

    return cands
