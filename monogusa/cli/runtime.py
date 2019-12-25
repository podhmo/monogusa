import typing as t
from types import ModuleType
import argparse
import inspect
from handofcats.injector import Injector
from monogusa.langhelpers import reify, run_with
from monogusa.dependencies import resolve_args, scan_module


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
        keywords = vars(args)
        action = keywords.pop("subcommand")

        positionals = resolve_args(action)
        return run_with(action, positionals, keywords, debug=debug)

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
            for fn in scan_module(module, where=where, _depth=_depth).commands:
                self.register(fn)
        return self._run(argv, debug=debug)


def create_parser(
    module: t.Optional[ModuleType] = None,
    *,
    where: t.Optional[str] = None,
    _depth: int = 2,
) -> argparse.ArgumentParser:
    driver = Driver()
    for fn in scan_module(module, where=where, _depth=_depth).commands:
        driver.register(fn)
    return driver.parser


def _get_summary(fn: t.Callable[..., t.Any]) -> t.Optional[str]:
    doc = inspect.getdoc(fn)
    if not doc:
        return doc
    return doc.split("\n\n", 1)[0]
