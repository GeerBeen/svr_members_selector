from fastapi import FastAPI, Header, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from pydantic import BaseModel
from DB.pydantic_models import RegisterPayload, LoginPayload
from DB.models import User
from DB.auth import hash_password, verify_password, generate_token
from DB.init_db.init_db import engine
from backend.pydantic_models import CouncilPayload
from backend.profile import Profile
from backend.algorithm import form_council
import uvicorn

from DB.init_db.init_db import init_db_on_first_start

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_on_first_start()
    yield


app = FastAPI(lifespan=lifespan)


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
    

@app.post('/get-council')
def get_council(payload: CouncilPayload):
    
    app_profile = Profile(
        orcid=payload.orcid,
        specialty=payload.specialty_id, 
        keywords=payload.keywords
    )

    try:
        council = form_council(app_profile, payload.amount, key=payload.key)
        res_list = [cand.orcid for cand in council]
        return {"orcid_list": res_list}
    
    except Exception as e:
        print(f"Помилка під час обробки запиту: {e}")
        raise HTTPException(
            status_code=500, 
            detail={"error": "Внутрішня помилка сервера.", "details": str(e)}
        )


def main():
    uvicorn.run(app)


if __name__ == '__main__':
    main()
