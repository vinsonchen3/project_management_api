from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as user_router
from app.api.v1.projects import router as project_router
from app.api.v1.tasks import router as task_router
from app.api.v1.comments import router as comment_router


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
app.include_router(user_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")
app.include_router(task_router, prefix="/api/v1")
app.include_router(comment_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"Hello": "world"}
