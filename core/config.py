from pydantic import BaseSettings, MongoDsn


class Settings(BaseSettings):
    BD_URL: MongoDsn = "mongodb://backend:123@localhost:27017"  # type: ignore
    SECRET_KEY: str = "secret key!"
