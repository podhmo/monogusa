import typing as t
import pathlib
from handofcats import as_command, Config
from magicalimport import import_module
from monogusa.web.codegen import codegen


@as_command(config=Config(ignore_expose=True))  # type: ignore
def run(
    target_module: str,
    *,
    dry_run: bool = False,
    dst: t.Optional[str] = None,
    ignore_only: bool = False,
) -> None:
    module = import_module(target_module, cwd=True)
    dst = dst or str(pathlib.Path.cwd())
    codegen(module, dst=dst, with_main=True, dry_run=dry_run, ignore_only=ignore_only)
