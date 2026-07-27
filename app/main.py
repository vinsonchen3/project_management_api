from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting app")
    yield
    print("shutting down app")


app = FastAPI(lifespan=lifespan, title="Project Management API")

# add routers here


@app.get("/")
def root():
    return {"Hello": "world"}
