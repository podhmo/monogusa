from __future__ import annotations
import typing as t
import typing_extensions as tx
from .events import MessageEvent

T = t.TypeVar("T")

# # need reactions
#
# - react with emoji
# - send message # with channel
# - reply message
# - direct reply


@tx.runtime_checkable
class reply_message(tx.Protocol):
    def __call__(self, ev: MessageEvent[T], text: str) -> None:
        ...


@tx.runtime_checkable
class send_message(tx.Protocol):
    def __call__(
        self, ev: MessageEvent[T], text: str, *, channel: t.Optional[str] = ...
    ) -> None:
        ...
