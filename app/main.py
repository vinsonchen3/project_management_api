from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting app")
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    yield
    print("shutting down app")


app = FastAPI(lifespan=lifespan, title="Project Management API")

# add routers here


@app.get("/")
def root():
    return {"Hello": "world"}
