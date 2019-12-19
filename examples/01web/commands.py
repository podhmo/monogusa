# TODO: support positional arguments
def hello(*, name: str = "world") -> None:
    print(f"Hello {name}")


def bye(*, name: str) -> None:
    print(f"Bye {name}")
