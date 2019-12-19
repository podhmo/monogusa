import typing as t
import sys
import re
import os.path
import dataclasses
from prestring.naming import pascalcase
from prestring.utils import LazyArguments

from . import _codeobject as codeobject
from ._codeobject import Module, as_string
from . import _fnspec as fnspec

# TODO: support dependencies


def create_schema_code(spec: fnspec.Fnspec) -> codeobject.Object:
    """
    generate code like below

    class <Name>(BaseModel):  # pydantic.BaseModel

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
                        "{}: {}  = {}",
                        name,
                        spec.type_str_of(typ),
                        spec.default_of(name),
                    )
                else:
                    raise ValueError(f"invalid kind. name={name}, kind={kind}")
        return m

    _emit_code.name = pascalcase(spec.name)
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
                m.stmt("{}({})", spec.fullname, LazyArguments(args))
                m.stmt("return s.dict()")
        return m

    _emit_code.name = spec.name  # update name
    return _emit_code


def create_main_code(*, where: t.Optional[str] = None) -> codeobject.Object:
    """
    generate main()
    """

    @codeobject.codeobject
    def main_code(m: Module, name: str) -> Module:
        with m.def_("main", "app: t.Optional[FastAPI]=None", return_type=None):
            m.from_("monogusa.web", "cli")
            with m.if_("app is None"):
                m.stmt("app = FastAPI()")
                m.stmt("app.include_router(router)")
            m.stmt(f"cli.run(app, where={as_string(where)})")

        m.stmt("app = FastAPI()")
        m.stmt("app.include_router(router)")
        with m.if_("__name__ == '__main__'"):
            m.stmt("main(app=app)")
        return m

    return main_code


def emit_routers(
    functions: t.List[t.Callable[..., t.Any]],
    *,
    with_main: bool = False,
    where: t.Optional[str] = None,
) -> Module:
    m = Module(import_unique=True)
    m.toplevel = m.submodule()
    m.sep()

    m.toplevel.import_("typing", as_="t")
    m.toplevel.from_("pydantic", "BaseModel")
    m.toplevel.from_("fastapi", "APIRouter", "Depends", "FastAPI")

    m.stmt("router = APIRouter()")
    m.sep()

    for fn in functions:
        spec = fnspec.fnspec(fn)

        m.toplevel.from_("monogusa.web", "runtime")

        # todo: separation as helper?
        if spec.module != "__main__":
            if _is_valid_module_name(spec.module):
                m.toplevel.import_(spec.module)
            else:
                m.toplevel.import_("magicalimport")
                valid_modname = _to_valid_module_name(spec.module)
                target_file_path = sys.modules[spec.module].__file__
                m.stmt(
                    "{} = magicalimport.import_module({!r}, here={!r})",
                    valid_modname,
                    os.path.basename(target_file_path),
                    os.path.dirname(target_file_path),
                )
                spec = dataclasses.replace(spec, _module=valid_modname)
                m.sep()

        schema_code = None
        if len(spec.parameters) > 0:
            schema_code = create_schema_code(spec)
            m.stmt(schema_code)

        view_code = create_view_code(spec, InputSchema=schema_code)
        m.stmt(view_code)

    if with_main:
        m.stmt(create_main_code(where=where))
    return m


# todo: helpers
def _is_valid_module_name(
    name: str, *, _rx=re.compile(r"^[_a-zA-Z][_a-zA-Z0-9]+$")
) -> bool:
    return _rx.match(name) is not None


def _to_valid_module_name(name: str, *, _ignore_rx=re.compile("[^0-9a-zA-Z_]+")) -> str:
    c = name[0]
    if c.isdigit():
        name = "n" + name
    elif not (c.isalpha() or c == "_"):
        name = "x" + name
    return _ignore_rx.sub("_", name.replace("-", "_"))
