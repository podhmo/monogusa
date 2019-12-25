from __future__ import annotations
import typing as t
import time
import contextlib
import dataclasses
import pydantic.main as pydantic_main
import pydantic.class_validators


@dataclasses.dataclass
class State:
    console: t.List[_OutputRow]
    start: float  # time.time()

    # shell's status code like value.
    # so the situation http status is 200 but status code != 0 is existed.
    status_code: int = 0

    def dict(self) -> t.Dict[str, t.Any]:
        return {
            "status_code": self.status_code,
            "duration": time.time() - self.start,
            "console": self.console,
        }


@contextlib.contextmanager
def handle(*, now: t.Optional[float] = None) -> t.Iterator[State]:
    box: t.List[_OutputRow] = []
    stdout = _JSONIO(box, port="stdout")
    stderr = _JSONIO(box, port="stderr")
    now = now or time.time()

    s = State(start=now, console=box)
    # TODO: use demux like interface, instead of redirect_xxx()
    with contextlib.redirect_stdout(stdout):  # type: ignore
        with contextlib.redirect_stderr(stderr):  # type: ignore
            try:
                yield s
            except Exception:
                # TODO: returning 500 response ?
                import traceback

                s.status_code = 1
                tb = traceback.format_exc()
                print(tb, file=stderr)


class _JSONIO:
    def __init__(self, box: t.List[_OutputRow], port: str = "stdout") -> None:
        self.box = box
        self.port = port

    def write(self, lines: str) -> None:
        if not lines:
            return
        data = _OutputRow.construct(port=self.port, lines=_as_list(lines))
        self.box.append(data)

    def writelines(self, lines: t.Iterable[str]) -> None:
        for line in lines:
            self.write(line)


# todo: move it?
class _OutputRow(pydantic_main.BaseModel):
    port: str
    lines: t.List[str]


class CommandOutput(pydantic_main.BaseModel):
    status_code: int = 0
    console: t.List[_OutputRow]
    duration: float

    @pydantic.class_validators.validator("console", always=True)
    def as_clean_list(cls, rows: t.List[_OutputRow]) -> t.List[_OutputRow]:
        return [row for row in rows if row.lines]


def _as_list(s: t.Union[t.List[str], str]) -> t.List[str]:
    if isinstance(s, list):
        return s

    s = s.rstrip()
    return s.split("\n") if s else []
