from fastapi import FastAPI
from api import roteadorEvento

petBack = FastAPI()
petBack.include_router(roteadorEvento)


@petBack.get("/")
def read_root():
    return {"Hello": "World"}
