from typing import Dict, List


def hello(*, name: str = "world") -> Dict[str, str]:
    return {"message": f"Hello {name}"}


def bye(*, name: str = "world") -> Dict[str, List[str]]:
    return [
        {"message": f"Bye {name}"},
        {"message": f"Bye {name}"},
        {"message": f"Bye {name}"},
    ]
