from fastapi import FastAPI, Header, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from pydantic import BaseModel
from DB.pydantic_models import RegisterPayload, LoginPayload
from DB.models import User
from DB.auth import hash_password, verify_password, generate_token
from DB.create_database import engine

app = FastAPI()


@app.post("/register")
def register(payload: RegisterPayload):
    with Session(engine) as session:
        if session.exec(select(User).where(User.username == payload.username)).first():
            raise HTTPException(400, "Користувач вже існує")

        user = User(
            username=payload.username,
            hashed_password=hash_password(payload.password),
        )
        session.add(user)
        session.commit()
        return {"msg": "Зареєстровано!"}


@app.post("/login")
def login(payload: LoginPayload):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == payload.username)).first()
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(401, "Неправильно")

        new_token = generate_token()
        user.token = new_token
        user.last_login_at = datetime.utcnow()
        session.add(user)
        session.commit()

        return {"token": new_token}
