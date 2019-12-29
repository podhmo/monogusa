# this module is generated by monogusa.web.codegen
import cli
from fastapi import (
    APIRouter,
    Depends,
    FastAPI
)
import typing as t
from pydantic import BaseModel
from monogusa.web import (
    runtime
)
import sqlalchemy.engine.base
import databases.core


async def db(database_url: str=Depends(cli.database_url)) -> cli.Database:
    return await cli.db(database_url)


def engine(database_url: str=Depends(cli.database_url)) -> cli.Engine:
    return cli.engine(database_url)


router = APIRouter()


@router.post("/init", response_model=runtime.CommandOutput)
def init(engine: sqlalchemy.engine.base.Engine=Depends(engine)) -> t.Dict[str, t.Any]:
    """
     init tables
    """
    with runtime.handle() as s:
        cli.init(engine)
    return s.dict()


class AddInput(BaseModel):
    text: str
    completed: bool  = 'False'


@router.post("/add", response_model=runtime.CommandOutput)
async def add(input: AddInput, db: databases.core.Database=Depends(db)) -> t.Dict[str, t.Any]:
    with runtime.handle() as s:
        await cli.add(db, **input.dict())
    return s.dict()


@router.post("/list", response_model=runtime.CommandOutput)
async def list(db: databases.core.Database=Depends(db)) -> t.Dict[str, t.Any]:
    with runtime.handle() as s:
        await cli.list(db)
    return s.dict()


def main(app: FastAPI):
    from monogusa.web import cli
    cli.run(app)


app = FastAPI()
app.include_router(router)


if __name__ == '__main__':
    main(app=app)