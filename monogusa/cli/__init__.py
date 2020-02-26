import typing as t
from types import ModuleType


def run(
    module: t.Optional[ModuleType] = None,
    *,
    filename: t.Optional[str] = None,
    args: t.Optional[t.List[str]] = None,
    setup: t.Optional[t.Callable[[], None]] = None,
    debug: bool = False,
    _depth: int = 3,
    ignore_only: bool = False,
) -> None:
    from monogusa.cli.runtime import Driver

    if setup is None:
        from monogusa.cli import defaultcomponent

        setup = defaultcomponent.setup
    setup()

    driver = Driver(prog=filename)
    driver.run(
        args,
        module=module,
        debug=debug,
        _depth=_depth,
        aggressive=True,
        ignore_only=ignore_only,
    )
