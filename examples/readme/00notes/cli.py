import os
import dotenv
from databases import Database
from sqlalchemy.engine import Engine
from monogusa import component, once
from monogusa import export_as_command

import crud
from models import metadata


def init(engine: Engine) -> None:
    """ init tables"""
    metadata.create_all(bind=engine)


add = export_as_command(crud.create_note, name="add")
list = export_as_command(crud.read_notes, name="list")


@once
@component
def database_url() -> str:
    dotenv.load_dotenv()
    return os.environ["DB_URL"]


@once
@component
async def db(database_url: str) -> Database:
    db = Database(database_url)
    await db.connect()
    return db


@component
def engine(database_url: str) -> Engine:
    import sqlalchemy

    return sqlalchemy.create_engine(
        database_url, connect_args={"check_same_thread": False}
    )
