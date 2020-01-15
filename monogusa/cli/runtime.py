import typing as t
from types import ModuleType
import argparse
import inspect
from handofcats.injector import Injector
from handofcats.customize import logging_setup
from monogusa.langhelpers import reify, run_with, run_with_async
from monogusa.dependencies import scan_module, resolve_args, resolve_args_async


class _HelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter
):
    pass


class Driver:
    def __init__(
        self,
        *,
        parser: t.Optional[argparse.ArgumentParser] = None,
        prog: t.Optional[str] = None,
        subcommand_title: str = "subcommands",
    ):
        self.parser = parser or argparse.ArgumentParser(
            prog=prog, formatter_class=_HelpFormatter
        )
        self.subcommand_title = subcommand_title

    @reify
    def subparsers(self) -> argparse._SubParsersAction:  # xxx (incorrect type?)
        subparesrs = self.parser.add_subparsers(
            title=self.subcommand_title, dest="subcommand"
        )
        subparesrs.required = True  # for py3.6
        return subparesrs

    def register(self, fn: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
        sub_parser = self.subparsers.add_parser(
            fn.__name__,
            help=_get_summary(fn),
            formatter_class=self.parser.formatter_class,
        )

        # NOTE: positional arguments are treated as component
        Injector(fn).inject(sub_parser, ignore_arguments=True)

        sub_parser.set_defaults(subcommand=fn)
        return fn

    def _run(self, argv: t.Optional[t.List[str]] = None, debug: bool = False) -> t.Any:
        activate_functions = [logging_setup(self.parser, debug=debug)]

        args = self.parser.parse_args(argv)
        keywords = vars(args).copy()

        for activate in activate_functions:
            activate(keywords)

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
        ignore_only: bool = False,
    ) -> t.Any:
        if aggressive or module:
            for fn in scan_module(
                module, where=where, _depth=_depth, ignore_only=ignore_only
            ).commands:
                self.register(fn)
        return self._run(argv, debug=debug)


class AsyncDriver(Driver):
    # override
    async def _run(
        self, argv: t.Optional[t.List[str]] = None, debug: bool = False
    ) -> t.Any:
        args = self.parser.parse_args(argv)
        keywords = vars(args).copy()
        action = keywords.pop("subcommand")

        positionals = await resolve_args_async(action)
        return await run_with_async(action, positionals, keywords, debug=debug)

    # override
    async def run(
        self,
        argv: t.Optional[t.List[str]] = None,
        *,
        aggressive: bool = False,
        where: t.Optional[str] = None,
        module: t.Optional[ModuleType] = None,
        _depth: int = 2,
        debug: bool = False,
        ignore_only: bool = False,
    ) -> t.Any:
        if aggressive or module:
            for fn in scan_module(
                module, where=where, _depth=_depth, ignore_only=ignore_only
            ).commands:
                self.register(fn)
        return await self._run(argv, debug=debug)


def create_parser(
    module: t.Optional[ModuleType] = None,
    *,
    where: t.Optional[str] = None,
    _depth: int = 2,
    ignore_only: bool = False,
) -> argparse.ArgumentParser:
    driver = Driver()
    for fn in scan_module(
        module, where=where, _depth=_depth, ignore_only=ignore_only
    ).commands:
        driver.register(fn)
    return driver.parser


def _get_summary(fn: t.Callable[..., t.Any]) -> t.Optional[str]:
    doc = inspect.getdoc(fn)
    if not doc:
        return doc
    return doc.split("\n\n", 1)[0]
