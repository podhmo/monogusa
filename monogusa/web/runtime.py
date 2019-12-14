import typing as t
import time
import contextlib
import dataclasses
from io import StringIO
import pydantic


@dataclasses.dataclass
class State:
    stdout: t.IO[str]
    stderr: t.IO[str]
    start: float  # time.time()


@contextlib.contextmanager
def handle(*, now: t.Optional[float] = None) -> t.Iterator[State]:
    stdout = StringIO()
    stderr = StringIO()
    now = now or time.time()

    # TODO: use demux like interface, instead of redirect_xxx()
    with contextlib.redirect_stdout(stdout):
        with contextlib.redirect_stderr(stderr):
            yield State(start=now, stdout=stdout, stderr=stderr)


# todo: move it?
class CommandOutput(pydantic.BaseModel):
    stdout: t.Union[t.List[str], str]
    stderr: t.Union[t.List[str], str]
    duration: float

    @pydantic.validator("stdout", "stderr", always=True)
    def as_clean_list(cls, s: t.Union[t.List[str], str]) -> t.List[str]:
        return _as_list(s)


def _as_list(s: t.Union[t.List[str], str]) -> t.List[str]:
    if isinstance(s, list):
        return s

    s = s.rstrip()
    return s.split("\n") if s else []
