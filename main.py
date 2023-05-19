from fastapi import FastAPI

petBack = FastAPI()


@petBack.get("/")
def read_root():
    return {"Hello": "World"}
