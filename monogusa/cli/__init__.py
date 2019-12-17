import typing as t
import os
from types import ModuleType


def run(
    module: t.Optional[ModuleType] = None,
    *,
    filename: t.Optional[str] = None,
    args: t.Optional[t.List[str]] = None,
    debug: bool = False,
    loglevel: t.Optional[str] = None,
    _depth: int = 3,
) -> None:
    from monogusa.cli.runtime import Driver

    if not debug:
        debug = bool(os.environ.get("DEBUG"))

    if loglevel is None:
        if os.environ.get("LOGGING"):
            loglevel = os.environ["LOGGING"]
    if loglevel is not None:
        import logging

        logging.basicConfig(level=getattr(logging, loglevel.upper()))

    driver = Driver(prog=filename)
    driver.run(args, module=module, debug=debug, _depth=_depth, aggressive=True)
