import typing as t
import dataclasses
from prestring.naming import pascalcase
from prestring.utils import LazyArguments

from . import helpers
from . import _codeobject as codeobject
from ._codeobject import Module
from . import _fnspec as fnspec

# TODO: support dependencies


def emit_routes(
    functions: t.List[t.Callable[..., t.Any]], *, m: Module, with_main: bool, where: str
) -> Module:
    m.toplevel.import_("typing", as_="t")
    m.toplevel.from_("pydantic", "BaseModel")
    m.toplevel.from_("fastapi", "APIRouter", "Depends")

    m.stmt("router = APIRouter()")
    m.sep()

    imported: t.Dict[str, str] = {}  # spec.module -> exact module name
    for fn in functions:
        spec = fnspec.fnspec(fn)

        m.toplevel.from_("monogusa.web", "runtime")

        if spec.module != "__main__":
            if spec.module not in imported:
                exact_module_name = helpers.emit_target_spec_import(
                    spec, where=where, m=m
                )
                imported[spec.module] = exact_module_name

            # update module path
            spec = dataclasses.replace(spec, _module=imported[spec.module])

        schema_code = None
        if len(spec.parameters) > 0:
            schema_code = create_input_schema_code(spec)
            m.stmt(schema_code)

        view_code = create_view_code(spec, InputSchema=schema_code)
        m.stmt(view_code)

    if with_main:
        m.stmt(main_code)
    return m


def create_input_schema_code(spec: fnspec.Fnspec) -> codeobject.Object:
    """
    generate code like below

    class <Name>Input(BaseModel):  # pydantic.BaseModel

        # fieds are filled by passed function's spec, something this.
        name: str
        age: int = 0
    """

    @codeobject.codeobject
    def _emit_code(m: Module, name: str) -> Module:
        with m.class_(name, "BaseModel"):
            if spec.doc is not None:
                m.docstring(
                    f"auto generated class from {spec.target_function.__module__}:{spec.name}"
                )

            if len(spec.parameters) == 0:
                m.stmt("pass")

            for name, typ in spec.parameters:
                kind = spec.kind_of(name)
                if kind == "args":
                    continue
                elif kind == "args_defaults":
                    continue
                elif kind == "kw":
                    m.stmt("{}: {}", name, spec.type_str_of(typ))
                elif kind == "kw_defaults":
                    m.stmt(
                        "{}: {}  = {!r}",
                        name,
                        spec.type_str_of(typ),
                        spec.default_of(name),
                    )
                else:
                    raise ValueError(f"invalid kind. name={name}, kind={kind}")
        return m

    _emit_code.name = f"{pascalcase(spec.name)}Input"
    return _emit_code


def create_view_code(
    spec: fnspec.Fnspec, *, InputSchema: t.Optional[codeobject.Object]
) -> codeobject.Object:
    """
    generate code like below

    @router.post("/<name>", response_model=runtime.CommandOutput)
    def <name>(input: <Name>) -> t.Dict[str, t.Any]:
        with runtime.handle() as s:
            <module>.<name>(**input.dict())
            return s.dict()
    """

    @codeobject.codeobject
    def _emit_code(m: Module, name: str) -> Module:
        # TODO: DI
        m.stmt('@router.post("/{}", response_model=runtime.CommandOutput)', spec.name)

        args = []
        if InputSchema is not None:
            args.append(f"input: {InputSchema}")

        with m.def_(name, *args, return_type="t.Dict[str, t.Any]"):
            if spec.doc is not None:
                m.docstring(spec.doc)
            with m.with_("runtime.handle() as s"):
                args = []
                if InputSchema is not None:
                    args.append("**input.dict()")
                    m.stmt("# TODO: support positional arguments? (DI)")
                m.stmt("{}({})", spec.fullname, LazyArguments(args))
                m.stmt("return s.dict()")
        return m

    _emit_code.name = spec.name  # update name
    return _emit_code


@codeobject.codeobject
def main_code(m: Module, name: str) -> Module:
    m.toplevel.from_("fastapi", "FastAPI")

    with m.def_("main", "app: FastAPI", return_type=None):
        m.from_("monogusa.web", "cli")
        m.stmt(f"cli.run(app)")

    m.stmt("app = FastAPI()")
    m.stmt("app.include_router(router)")
    with m.if_("__name__ == '__main__'"):
        m.stmt("main(app=app)")
    return m
