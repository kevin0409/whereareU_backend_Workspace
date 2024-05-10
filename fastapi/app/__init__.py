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
    from . import routes
    app.include_router(routes.router)

    routes.sched.start()

    return app

@app.exception_handler(HTTPException)
async def http_exception_handler(exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )