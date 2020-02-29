import typing as t
from prestring.naming import pascalcase
from prestring.utils import LazyArguments

from . import helpers
from . import _codeobject as codeobject
from ._codeobject import Module
from . import _fnspec as fnspec


def emit_routes(
    m: Module,
    *,
    functions: t.List[t.Callable[..., t.Any]],
    spec_map: t.Dict[str, fnspec.Fnspec],
    where: str,
) -> Module:
    m.toplevel.import_("typing", as_="t")
    m.toplevel.from_("pydantic", "BaseModel")
    m.toplevel.from_("fastapi", "APIRouter", "Depends")

    m.stmt("router = APIRouter()")
    m.sep()

    for fn in functions:
        spec = spec_map[fn.__name__]

        m.toplevel.from_("monogusa.web", "runtime")

        schema_code = None
        if len(spec.keyword_arguments) > 0:
            schema_code = create_input_schema_code(spec)
            m.stmt(schema_code)

        view_code = create_view_code(spec, InputSchema=schema_code, spec_map=spec_map)
        m.stmt(view_code)
    return m


def create_input_schema_code(spec: fnspec.Fnspec,) -> codeobject.Object:
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
                    f"auto generated class from {spec.body.__module__}:{spec.name}"
                )

            if len(spec.keyword_arguments) == 0:
                m.stmt("pass")

            for name, typ, kind in spec.parameters:
                if kind == "args":
                    continue
                elif kind == "args_defaults":
                    continue
                elif kind == "kw":
                    m.stmt("{}: {}", name, spec.type_str_of(typ))
                elif kind == "kw_defaults":
                    m.stmt(
                        "{}: {} = {}",
                        name,
                        spec.type_str_of(typ),
                        spec.default_str_of(name),
                    )
                else:
                    raise ValueError(f"invalid kind. name={name}, kind={kind}")
        return m

    _emit_code.name = f"{pascalcase(spec.command_name)}Input"
    return _emit_code


def create_view_code(
    spec: fnspec.Fnspec,
    *,
    InputSchema: t.Optional[codeobject.Object],
    spec_map: t.Dict[str, fnspec.Fnspec],
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
        m.stmt(
            '@router.post("/{}", response_model=runtime.CommandOutput)',
            spec.command_name,
        )

        args = []
        if InputSchema is not None:
            args.append(f"input: {InputSchema}")
        #  for di
        for argname, typ, _ in spec.arguments:
            if typ.__module__ != "builtins":
                m.toplevel.import_(typ.__module__)
            args.append(helpers._spec_to_arg_value__with_depends(spec_map[argname]))

        with m.def_(
            name,
            *args,
            return_type="t.Dict[str, t.Any]",
            async_=spec.is_coroutinefunction,
        ):

            if spec.doc is not None:
                m.docstring(spec.doc)
            with m.with_("runtime.handle() as s"):
                args = [argname for argname, _, _ in spec.arguments]
                if InputSchema is not None:
                    args.append("**input.dict()")

                prefix = "await " if spec.is_coroutinefunction else ""
                m.stmt("{}{}({})", prefix, spec.fullname, LazyArguments(args))
            m.stmt("return s.dict()")
        return m

    _emit_code.name = spec.command_name  # update name
    return _emit_code
