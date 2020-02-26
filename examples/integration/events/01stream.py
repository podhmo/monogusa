import typing as t
from monogusa.events import subscribe, MessageEvent
from monogusa import reactions


@subscribe(MessageEvent[t.Any])
def on_message(
    ev: MessageEvent[t.Any],
    reply: reactions.reply_message,
    send: reactions.send_message,
) -> None:
    reply(ev, f"got {ev.content}")
    send(ev, f"{ev.content}", channel="random")


def read() -> None:
    """fake event stream"""
    from monogusa.cli.events import console_stream, run_stream

    examples = """\
Message, hello
Message, byebye
"""
    run_stream(console_stream(default=examples, sep=","))


if __name__ == "__main__":
    from monogusa.cli import run

    run()
