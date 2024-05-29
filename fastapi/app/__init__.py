from fastapi import FastAPI, Depends, Path, HTTPException
from pydantic import BaseModel
from .database import Database
from sqlalchemy import *
from mangum import Mangum
from fastapi.responses import JSONResponse


# FastAPI 인스턴스 생성
app = FastAPI()
handler = Mangum(app)
engine = Database()
session = engine.get_session()

# 라우트 설정
def create_app():
    from . import routes2
    app.include_router(routes2.router)

    routes2.sched.start()

    return app