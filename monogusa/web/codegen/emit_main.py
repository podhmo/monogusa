import typing as t

from . import _codeobject as codeobject
from ._codeobject import Module
from . import _fnspec as fnspec

from .emit_routes import emit_routes
from .emit_components import emit_components


def emit_main(
    m: Module,
    *,
    functions: t.List[t.Callable[..., t.Any]],
    components: t.List[t.Callable[..., t.Any]],
    spec_map: t.Dict[str, fnspec.Fnspec],
    where: str,
    with_main: bool,
) -> Module:
    m = emit_components(m, components=components, where=where, spec_map=spec_map)
    m = emit_routes(m, functions=functions, where=where, spec_map=spec_map)
    if with_main:
        m.stmt(main_code)
    return m


@codeobject.codeobject
def main_code(m: Module, name: str) -> Module:
    m.toplevel.from_("fastapi", "FastAPI")

    with m.def_("main", "app: FastAPI", return_type=None):
        m.from_("monogusa.web", "cli")
        m.stmt(f"cli.run(app)")

    m.stmt("app = FastAPI()")
    m.stmt("app.include_router(router)")
    m.sep()

    with m.if_("__name__ == '__main__'"):
        m.stmt("main(app=app)")
    return m
