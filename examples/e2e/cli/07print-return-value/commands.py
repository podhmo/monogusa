def hello(*, name: str = "world") -> str:
    return {"message": f"Hello {name}"}


def bye(*, name: str = "world") -> str:
    return [
        {"message": f"Bye {name}"},
        {"message": f"Bye {name}"},
        {"message": f"Bye {name}"},
    ]
