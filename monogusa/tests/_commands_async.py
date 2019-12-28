import typing as t
from functools import partial
import asyncio
from io import StringIO

from monogusa import component, ignore


async def hello(print_: t.Callable[..., t.Any]) -> None:
    await asyncio.sleep(0.1)
    print_("hello")
    await asyncio.sleep(0.1)
    print_("end")


OUTPUT = StringIO()


@ignore
def cleaup() -> None:
    OUTPUT.seek(0)


@component
def print_() -> t.Callable[..., t.Any]:
    global OUTPUT
    return partial(print, file=OUTPUT)
