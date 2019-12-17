import typing as t
import os
from types import ModuleType


def run(
    module: t.Optional[ModuleType] = None,
    *,
    filename: t.Optional[str] = None,
    args: t.Optional[t.List[str]] = None,
    _depth: int = 3,
) -> None:
    from monogusa.cli.runtime import Driver

    debug = bool(os.environ.get("DEBUG"))
    if os.environ.get("LOGGING"):
        import logging

        logging.basicConfig(level=getattr(logging, os.environ["LOGGING"].upper()))
    driver = Driver(prog=filename)
    driver.run(args, module=module, debug=debug, _depth=_depth, aggressive=True)
