from handofcats import as_command
from magicalimport import import_module
from monogusa.cli.runtime import collect_commands
from monogusa.web.codegen import emit_routers


@as_command  # type: ignore
def run(target_module: str, *, with_main: bool = False) -> None:
    module = import_module(target_module, cwd=True)
    fns = list(collect_commands(module))
    print(emit_routers(fns, with_main=with_main))
