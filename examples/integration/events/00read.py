import typing as t
from monogusa import events
from monogusa.events import subscribe


@subscribe(events.MessageEvent[t.Any])
def on_message(ev: events.MessageEvent[t.Any]) -> None:
    print("!", ev.content)


def read() -> None:
    import sys

    for line in sys.stdin:
        event_type, message = [x.strip() for x in line.strip().split(",", 1)]
        if event_type == "message":
            ev: events.Event[t.Any] = events.MessageEvent.from_text(message)
            subscribe.send(ev)
        else:
            ev = events.UnknownEvent.from_text(message)
        subscribe.send(ev)
