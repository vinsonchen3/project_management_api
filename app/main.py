from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Project Management API")

# add routers here


@app.get("/")
def root():
    return {"Hello": "world"}
