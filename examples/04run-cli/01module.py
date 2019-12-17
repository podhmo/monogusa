def hello(*, name: str) -> None:
    print(f"hello {name}")


if __name__ == "__main__":
    import sys
    from monogusa.cli import run

    run(sys.modules[__name__])
