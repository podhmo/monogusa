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
    m, router = emit_routes(m, functions=functions, where=where, spec_map=spec_map)
    if with_main:
        m.stmt(create_main_code(router))
    return m


def create_main_code(router: codeobject.Symbol) -> codeobject.Object:
    @codeobject.codeobject
    def main_code(m: Module, name: str) -> Module:
        FastAPI = m.toplevel.from_("fastapi").import_("FastAPI")

        app = codeobject.Symbol("app")
        with m.def_("main", f"{app}: {FastAPI}", return_type=None) as main:
            cli = m.from_("monogusa.web").import_("cli")
            m.sep()
            m.stmt(cli.run(app))

        app = m.let("app", FastAPI())
        m.stmt(app.include_router(router))
        m.sep()

        with m.if_("__name__ == '__main__'"):
            m.stmt(main(app=app))
        return m

    return main_code
