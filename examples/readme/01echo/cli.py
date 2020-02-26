import typing as t
from monogusa import events
from monogusa import reactions


@events.subscribe(events.MessageEvent[t.Any])
def on_message(ev: events.MessageEvent[t.Any], r: reactions.reply_message) -> None:
    r(ev, f"got {ev.content}")
