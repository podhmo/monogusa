def hello(*, name: str) -> None:
    print(f"hello {name}")


if __name__ == "__main__":
    from monogusa.cli import run

    run()
