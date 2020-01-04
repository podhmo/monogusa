import typing as t


def hello(*, name: str, nickname: t.Optional[str] = None) -> None:
    print(f"hello, {nickname or name}")
