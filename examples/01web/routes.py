import typing as t
from magicalimport import import_module
from fastapi import APIRouter
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
        return s.dict()


class ByeInput(BaseModel):
    name: str


@router.post("/bye", response_model=runtime.CommandOutput)
def bye(input: ByeInput) -> t.Dict[str, t.Any]:
    with runtime.handle() as s:
        commands.bye(**input.dict())  # TODO: support positional arguments?
        return s.dict()
