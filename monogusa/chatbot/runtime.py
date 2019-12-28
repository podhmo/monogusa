import typing as t
import sys
import argparse
import contextlib
import shlex
import logging
from io import StringIO

logger = logging.getLogger(__name__)


class Exit(Exception):
    pass


class ExitExceptionParser(argparse.ArgumentParser):
    # NOTE: the method of base class, return type is t.NoReturn, so ignore it.
    def exit(  # type:ignore
        self, status: int = 0, message: t.Optional[str] = None
    ) -> None:
        if message:
            # TODO: debug?
            self._print_message(message, sys.stderr)
        if message is not None:
            raise Exit(message)


def parse(text: str, *, name: str) -> t.List[str]:
    return shlex.split(text.split(name, 1)[1], posix=True)


@contextlib.contextmanager
def handle() -> t.Iterator[t.List[str]]:
    output_list: t.List[str] = []
    o = StringIO()
    with contextlib.redirect_stdout(o):
        with contextlib.redirect_stderr(o):
            try:
                yield output_list
            except Exit as e:
                logger.debug("exit: %r", e)
            except Exception:
                import traceback

                tb = traceback.format_exc()
                print(tb, file=o)

    output = o.getvalue()
    if output.strip():
        output_list.append(output)
