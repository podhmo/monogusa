from monogusa import only, ignore


@only
def foo() -> None:
    pass


def bar() -> None:
    pass


@ignore
def boo() -> None:
    pass


def yoo() -> None:
    pass
