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

    # shell's status code like value.
    # so the situation http status is 200 but status code != 0 is existed.
    status_code: int = 0

    def dict(self) -> t.Dict[str, t.Any]:
        return {
            "status_code": self.status_code,
            "duration": time.time() - self.start,
            "stdout": self.stdout.getvalue(),
            "stderr": self.stderr.getvalue(),
        }


@contextlib.contextmanager
def handle(*, now: t.Optional[float] = None) -> t.Iterator[State]:
    stdout = StringIO()
    stderr = StringIO()
    now = now or time.time()

    s = State(start=now, stdout=stdout, stderr=stderr)
    # TODO: use demux like interface, instead of redirect_xxx()
    with contextlib.redirect_stdout(stdout):
        with contextlib.redirect_stderr(stderr):
            try:
                yield s
            except Exception:
                # TODO: returning 500 response ?
                import traceback

                s.status_code = 1
                tb = traceback.format_exc()
                print(tb, file=stderr)


# todo: move it?
class CommandOutput(pydantic_main.BaseModel):
    status_code: int = 0
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
