def hello(*, name: str = "world") -> None:
    print(f"Hello {name}")


def bye(*, name: str = "world") -> None:
    print(f"Bye {name}")
