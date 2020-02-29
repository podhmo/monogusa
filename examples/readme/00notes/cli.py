import os
import dotenv
from databases import Database
from monogusa import component, once
from monogusa import export_as_command

import crud
from models import metadata


########################################
# commands
########################################


add = export_as_command(crud.create_note)
list = export_as_command(crud.read_notes)


def init(database_url: str) -> None:
    """ init tables"""
    import sqlalchemy

    engine = sqlalchemy.create_engine(
        database_url, connect_args={"check_same_thread": False}
    )
    metadata.create_all(bind=engine)


########################################
# components
########################################


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
