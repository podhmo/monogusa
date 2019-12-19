import typing as t
from types import ModuleType
import sys
import argparse
import inspect
from handofcats.injector import Injector
from monogusa.langhelpers import reify
from monogusa.dependencies import resolve_args, is_component


class Driver:
    def __init__(
        self,
        *,
        parser: t.Optional[argparse.ArgumentParser] = None,
        prog: t.Optional[str] = None,
        subcommand_title: str = "subcommands",
    ):
        self.parser = parser or argparse.ArgumentParser(prog=prog)
        self.subcommand_title = subcommand_title

    @reify
    def subparsers(self) -> argparse._SubParsersAction:  # xxx (incorrect type?)
        subparesrs = self.parser.add_subparsers(
            title=self.subcommand_title, dest="subcommand"
        )
        subparesrs.required = True  # for py3.6
        return subparesrs

    def register(self, fn: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
        sub_parser = self.subparsers.add_parser(fn.__name__, help=_get_summary(fn))

        # NOTE: positional arguments are treated as component
        Injector(fn).inject(sub_parser, ignore_arguments=True)

        sub_parser.set_defaults(subcommand=fn)
        return fn

    def _run(self, argv: t.Optional[t.List[str]] = None, debug: bool = False) -> t.Any:
        args = self.parser.parse_args(argv)
        params = vars(args)
        action = params.pop("subcommand")

        positionals = resolve_args(action)

        if inspect.iscoroutinefunction(action):
            import asyncio

            return asyncio.run(action(*positionals, **params), debug=debug)
        else:
            return action(*positionals, **params)

    def run(
        self,
        argv: t.Optional[t.List[str]] = None,
        *,
        aggressive: bool = False,
        where: t.Optional[str] = None,
        module: t.Optional[ModuleType] = None,
        _depth: int = 2,
        debug: bool = False,
    ) -> t.Any:
        if aggressive or module:
            for fn in collect_commands(module, where=where, _depth=_depth):
                self.register(fn)
        return self._run(argv, debug=debug)


def collect_commands(
    module: t.Optional[ModuleType] = None,
    where: t.Optional[str] = None,
    _depth: int = 1,
) -> t.Iterable[t.Callable[..., t.Any]]:
    if module is not None:
        _globals = module.__dict__
    else:
        frame = sys._getframe(_depth)  # black magic
        _globals = frame.f_globals
    where = _globals["__name__"]
    for name, v in _globals.items():
        if name.startswith("_"):
            continue
        if is_component(v):
            continue
        if inspect.isfunction(v) and v.__module__ == where:
            yield v


def create_parser(
    module: t.Optional[ModuleType] = None,
    *,
    where: t.Optional[str] = None,
    _depth: int = 2,
) -> argparse.ArgumentParser:
    driver = Driver()
    for fn in collect_commands(module, where=where, _depth=_depth):
        driver.register(fn)
    return driver.parser


def _get_summary(fn: t.Callable[..., t.Any]) -> t.Optional[str]:
    doc = inspect.getdoc(fn)
    if not doc:
        return doc
    return doc.split("\n\n", 1)[0]
