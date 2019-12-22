from __future__ import annotations
import typing as t
import json

from monogusa.langhelpers import reify
from monogusa import component


def list(notes: Store, *, uncompleted: bool = False):
    """list notes"""
    data = notes.data
    if uncompleted:
        data = [note for note in notes.data if not note["completed"]]

    print(json.dumps(data, indent=2, ensure_ascii=False))


@component
def notes() -> Store:
    import pathlib

    return Store(pathlib.Path(__file__).parent / "data/notes.json")


class Store:
    def __init__(self, path: str) -> None:
        self.path = path

    @reify
    def data(self) -> t.Mapping:
        with open(self.path) as rf:
            return json.load(rf)
