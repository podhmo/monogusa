import typing as t
import slacker
from slackbot.dispatcher import Message

from monogusa import events
from monogusa import reactions


def _is_bot_message(ev: events.MessageEvent[Message]) -> bool:
    return bool(ev.raw.body.get("bot_id"))


class MessageHandler:
    def __init__(self, token: str):
        self.client = slacker.Slacker(token)

    def reply_message(self, ev: events.MessageEvent[Message], text: str) -> None:
        if _is_bot_message(ev):
            return
        ev.raw.reply(text)

    def send_message(
        self,
        ev: events.MessageEvent[Message],
        text: str,
        *,
        channel: t.Optional[str] = "random"
    ) -> None:
        if _is_bot_message(ev):
            return
        self.client.chat.post_message(channel, text)


def setup(token: str) -> None:
    from monogusa import default_once

    handler = MessageHandler(token)

    @default_once
    def get_reply_function() -> reactions.reply_message:
        return handler.reply_message

    @default_once
    def get_send_function() -> reactions.send_message:
        return handler.send_message
