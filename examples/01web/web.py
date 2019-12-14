import typing as t
import time
from magicalimport import import_module
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from monogusa.web import runtime

commands = import_module("./commands.py", here=__file__)
router = APIRouter()


class HelloInput(BaseModel):
    name: str


@router.post("/hello", response_model=runtime.CommandOutput)
def hello(input: HelloInput) -> t.Dict[str, t.Any]:
    with runtime.handle() as s:
        commands.hello(**input.dict())  # TODO: support positional arguments?
        return {
            "duration": time.time() - s.start,
            "stdout": s.stdout.getvalue(),
            "stderr": s.stderr.getvalue(),
        }


class ByeInput(BaseModel):
    name: str


@router.post("/bye", response_model=runtime.CommandOutput)
def bye(input: ByeInput) -> t.Dict[str, t.Any]:
    with runtime.handle() as s:
        commands.bye(**input.dict())  # TODO: support positional arguments?
        return {
            "duration": time.time() - s.start,
            "stdout": s.stdout.getvalue(),
            "stderr": s.stderr.getvalue(),
        }


app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    from monogusa.web import cli

    cli.run(app)
