from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine
from app.api.v1.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting app")
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    yield
    print("shutting down app")


app = FastAPI(lifespan=lifespan, title="Project Management API")

# add routers here
app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"Hello": "world"}
