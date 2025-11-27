import json
from sqlmodel import Session, select, SQLModel, create_engine
from DB.models import (
    Institution, Specialty, Candidate, Keyword, CandidateKeyword, User
)
from typing import List, Dict, Set
from pathlib import Path
from DB.auth import hash_password
import os
from DB.init_db.database import create_db_and_tables

DATA_DIR = Path(__file__).resolve().parent
from DB.init_db.database import engine


def create_default_admin():
    with Session(engine) as session:
        if session.exec(select(User).where(User.username == "admin")).first():
            return
        admin = User(username="admin", hashed_password=hash_password("admin"), is_admin=True)
        session.add(admin)
        session.commit()
        print("Адмін створений (admin/admin)")


def get_session():
    with Session(engine) as session:
        yield session


def load_json(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def import_institutions(session: Session, institutions: List[Dict]):
    print(f"Імпорт {len(institutions)} закладів...")
    for inst in institutions:
        if not session.get(Institution, inst["edrpou"]):
            session.add(Institution(edrpou=inst["edrpou"], name=inst["name"]))
    session.commit()
    print("Заклади додано.")


def import_specialties(session: Session, specialties: List[str]):
    print(f"Імпорт {len(specialties)} спеціальностей...")
    for spec in specialties:
        parts = spec.strip().split(" ", 1)
        code = parts[0] if len(parts) > 0 else ""
        name = parts[1] if len(parts) > 1 else code

        if code and not session.exec(select(Specialty).where(Specialty.code == code)).first():
            session.add(Specialty(code=code, name=name))
    session.commit()
    print("Спеціальності додано.")


def import_candidates_and_keywords(session: Session, people: List[Dict], batch_size: int = 100):
    print(f"Імпорт {len(people)} кандидатів (батчами по {batch_size})...")

    # Кеш спеціальностей
    specialty_cache = {s.code: s.id for s in session.exec(select(Specialty)).all()}
    keyword_cache: Dict[str, int] = {}
    added = 0
    skipped = 0
    batch = []

    for person in people:
        orcid = person.get("orcid")
        name = person.get("name")
        faculty = person.get("faculty")
        hei_edrpou = person.get("hei_edrpou")
        degree_spec = person.get("degreeSpec", "")
        raw_keywords = person.get("keywords", [])

        # === ПРОПУСК НЕПОВНИХ ===
        if not all([orcid, name, hei_edrpou, degree_spec]):
            skipped += 1
            continue

        # === УНІКАЛЬНІ ключові слова ===
        keywords = list({k.strip() for k in raw_keywords if k and k.strip()})

        # === Перевірка дубля ===
        if session.get(Candidate, orcid):
            skipped += 1
            continue

        # === Спеціальність ===
        code = degree_spec.split(" ", 1)[0]
        spec_id = specialty_cache.get(code)
        if not spec_id:
            skipped += 1
            continue

        # === Додаємо кандидата ===
        candidate = Candidate(
            orcid=orcid,
            name=name,
            faculty=faculty,
            hei_edrpou=hei_edrpou,
            degree_spec_id=spec_id
        )
        session.add(candidate)

        # === Кешуємо ключові слова ===
        for word in keywords:
            if word not in keyword_cache:
                existing = session.exec(select(Keyword.id).where(Keyword.word == word)).first()
                keyword_cache[word] = existing[0] if existing else None

        batch.append((orcid, keywords))
        added += 1

        # === КОЖНІ batch_size — commit ===
        if len(batch) >= batch_size:
            _commit_batch(session, batch, keyword_cache)
            batch.clear()
            print(f"Додано {added}, пропущено {skipped}")

    # Останній батч
    if batch:
        _commit_batch(session, batch, keyword_cache)
        print(f"Додано {added}, пропущено {skipped}")

    print(f"ГОТОВО: додано {added}, пропущено {skipped}")


def _commit_batch(session: Session, batch: List[tuple], keyword_cache: Dict[str, int]):
    # 1. Додаємо нові ключові слова
    new_keywords = [
        Keyword(word=word)
        for word, kid in keyword_cache.items()
        if kid is None
    ]
    if new_keywords:
        session.add_all(new_keywords)
        session.flush()
        for kw in new_keywords:
            keyword_cache[kw.word] = kw.id

    # 2. УНІКАЛЬНІ зв’язки
    seen: Set[tuple] = set()
    links = []
    for orcid, keywords in batch:
        for word in keywords:
            if word not in keyword_cache:
                continue
            kid = keyword_cache[word]
            key = (orcid, kid)
            if key not in seen:
                seen.add(key)
                links.append(CandidateKeyword(candidate_orcid=orcid, keyword_id=kid))

    if links:
        session.add_all(links)
    session.commit()


# === ГОЛОВНА ФУНКЦІЯ ===
def insert_values():
    # 1. Завантажуємо JSON
    try:
        people = load_json(str(DATA_DIR / "unique_people.json"))
        institutions = load_json(str(DATA_DIR / "unique_institutions.json"))
        specialties = load_json(str(DATA_DIR / "unique_specialties.json"))
    except FileNotFoundError as e:
        print(f"Файл не знайдено: {e}\n\n ФАЙЛИ ")
        return

    # 2. Імпорт
    with Session(engine) as session:
        import_institutions(session, institutions)
        import_specialties(session, specialties)
        import_candidates_and_keywords(session, people, batch_size=200)

    print("ІМПОРТ ЗАВЕРШЕНО!")


def is_db_empty() -> bool:
    with Session(engine) as session:
        return session.exec(select(Candidate)).first() is None


DB_PATH = "defense.db"


def init_db_on_first_start():
    create_db_and_tables()
    # 1. Завжди створюємо таблиці — це безпечно
    print("Таблиці створено або вже існують")

    # 2. Перевіряємо, чи є дані в БД — це 100% надійно
    with Session(engine) as session:
        has_candidates = session.exec(select(Candidate)).first() is not None
        has_institutions = session.exec(select(Institution)).first() is not None

        if has_candidates or has_institutions:
            print("БД вже містить дані — імпорт пропущено")
            create_default_admin()  # тільки адміна, якщо нема
            return

    # 3. Якщо БД порожня — робимо повний імпорт
    print("БД порожня — запускаємо перший імпорт даних...")
    create_default_admin()
    insert_values()
    print("Перший запуск завершено!")
