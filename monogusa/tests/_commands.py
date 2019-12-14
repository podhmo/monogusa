# TODO: support positional arguments
def hello(*, name: str = "world") -> None:
    """hello world, example"""
    print(f"Hello {name}")


def bye(*, name: str = "world") -> None:
    """byebye, example"""
    print(f"Bye {name}")
