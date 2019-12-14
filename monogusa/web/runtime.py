import typing as t
import time
import contextlib
import dataclasses
from io import StringIO
import pydantic.main as pydantic_main
import pydantic.class_validators


@dataclasses.dataclass
class State:
    stdout: StringIO
    stderr: StringIO
    start: float  # time.time()

    def dict(self) -> t.Dict[str, t.Any]:
        return {
            "duration": time.time() - self.start,
            "stdout": self.stdout.getvalue(),
            "stderr": self.stderr.getvalue(),
        }


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
class CommandOutput(pydantic_main.BaseModel):
    stdout: t.Union[t.List[str], str]
    stderr: t.Union[t.List[str], str]
    duration: float

    @pydantic.class_validators.validator("stdout", "stderr", always=True)
    def as_clean_list(cls, s: t.Union[t.List[str], str]) -> t.List[str]:
        return _as_list(s)


def _as_list(s: t.Union[t.List[str], str]) -> t.List[str]:
    if isinstance(s, list):
        return s

    s = s.rstrip()
    return s.split("\n") if s else []
