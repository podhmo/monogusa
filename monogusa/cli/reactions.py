import typing as t
from monogusa import events


def reply_message(ev: events.MessageEvent[t.Any], text: str) -> None:
    print(f"reply message: {text}")


def send_message(
    ev: events.MessageEvent[t.Any], text: str, *, channel: t.Optional[str] = "default"
) -> None:
    print(f"send message({channel}): {text}")
