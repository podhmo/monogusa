from __future__ import annotations
import typing as t
import typing_extensions as tx
from collections import defaultdict
import dataclasses

from .langhelpers import reify
from .dependencies import ignore, _get_fullargspec


T = t.TypeVar("T")


@dataclasses.dataclass
class MessageEvent(t.Generic[T]):
    content: str
    raw: T

    @classmethod
    def from_text(cls, text: str) -> MessageEvent[t.Any]:
        raw: t.Any = None
        return cls(content=text, raw=raw)


@dataclasses.dataclass
class UnknownEvent(t.Generic[T]):
    content: str
    raw: T
    _type: str = "?"  # todo: type

    @classmethod
    def from_text(cls, text: str) -> UnknownEvent[t.Any]:
        raw: t.Any = None
        return cls(content=text, raw=raw)


# TODO: async support
Event = t.Union[MessageEvent[T], UnknownEvent[T]]


class Reaction(tx.Protocol):
    def __call__(self, ev: Event[T], *args: t.Any) -> t.Any:
        pass


LooseReaction = t.Callable[..., t.Any]
HandlerMap = t.Dict[t.Type[Event[T]], t.List[Reaction]]


class Subscription:
    def __init__(self, *, runtime_check: bool) -> None:
        self.runtime_check = runtime_check

    @reify
    def handler_map(self) -> HandlerMap[T]:
        return defaultdict(list)

    def __call__(
        self, event_type: t.Type[Event[T]]
    ) -> t.Callable[[LooseReaction], Reaction]:
        def _wrapped(fn: LooseReaction) -> Reaction:
            typ = event_type
            if hasattr(event_type, "__origin__"):
                typ = typ.__origin__  # type: ignore

            if self.runtime_check:
                argspec = _get_fullargspec(fn)
                for x in argspec.args:
                    arg_type = argspec.annotations[x]
                    if hasattr(arg_type, "__origin__"):
                        arg_type = arg_type.__origin__
                    if arg_type == typ:
                        break
                else:
                    raise ValueError(
                        "unexpected reaction function, please include {!r} in arguments",
                        typ,
                    )

            self.handler_map[typ].append(t.cast(Reaction, fn))

            return ignore(fn)

        return _wrapped

    def send(self, ev: Event[T]) -> None:
        from .dependencies import resolve_args

        handlers = self.handler_map[ev.__class__]

        # TODO: async
        for h in handlers:
            # TODO: cache
            args = resolve_args(h, i=1)
            h(ev, *(args[1:]))


# TODO: remove global variable
subscribe = Subscription(runtime_check=True)
