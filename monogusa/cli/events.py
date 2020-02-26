from __future__ import annotations
import typing as t
import sys
import os
import io
import logging
from prestring.naming import titleize
from monogusa import events

logger = logging.getLogger(__name__)


class Translator:
    def __init__(
        self, g: t.Optional[t.Dict[str, t.Any]] = None, *, sep: str = ":"
    ) -> None:
        self.sep = sep

    def translate(self, line: str) -> events.Event[None]:
        typ, line = [x.strip() for x in line.rstrip().split(self.sep, 1)]

        return (
            getattr(events, f"{titleize(typ)}Event", None) or events.UnknownEvent
        ).from_text(line)


def _stdin_or_fake_stream(default: t.Union[str, io.StringIO]) -> t.IO[str]:
    if not os.isatty(sys.stdin.fileno()):
        return sys.stdin

    if isinstance(default, io.StringIO):
        o = default
    else:
        o = io.StringIO()
        o.write(str(default))
    if not o.getvalue().endswith("\n"):
        o.write("\n")
    o.seek(0)
    return o


def console_stream(*, default: str, sep: str = ":") -> t.Iterator[events.Event[None]]:
    translate = Translator(sep=sep).translate
    stream = _stdin_or_fake_stream(default)

    for line in stream:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue

        logger.info(f"<- %r", line)
        yield translate(line)


def run_stream(
    stream: t.Iterator[events.Event[None]],
    *,
    send: t.Optional[t.Callable[[events.Event[t.Any]], None]] = None,
) -> None:
    send = send or events.subscribe.send
    for ev in stream:
        send(ev)
