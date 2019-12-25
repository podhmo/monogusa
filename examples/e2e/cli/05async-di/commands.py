from __future__ import annotations
import asyncio
import dataclasses
from monogusa import component


async def hello(db: DB, *, name: str = "world") -> None:
    await db.save(f"hello {name}")


@component
def registry(db: DB) -> Registry:
    return Registry(db=db)


@component
async def db() -> Registry:
    db = DB()
    await db.connect()
    return db


@dataclasses.dataclass
class Registry:
    db: DB


class DB:
    def __init__(self) -> None:
        self.connection = None

    async def connect(self) -> None:
        await asyncio.sleep(0.1)
        self.connection = Connection()

    async def save(self, message: str) -> None:
        if self.connection is None:
            raise RuntimeError("please calling connect()")
        await asyncio.sleep(0.1)
        print(message, file=self.connection)


class Connection:
    def write(self, text: str) -> int:
        if text == "\n":
            return 0
        print(f"save: {text}")
        return -1
