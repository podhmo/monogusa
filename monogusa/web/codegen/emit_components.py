import typing as t
from prestring.utils import LazyArguments
from prestring.utils import _type_value

from . import helpers

from . import _fnspec as fnspec
from . import _codeobject as codeobject
from ._codeobject import Module


def emit_components(
    m: Module,
    *,
    components: t.List[t.Callable[..., t.Any]],
    spec_map: t.Dict[str, fnspec.Fnspec],
    where: str,
) -> Module:
    m.toplevel.from_("fastapi", "Depends")

    # sub
    spec_map = {
        component.__name__: spec_map[component.__name__] for component in components
    }
    code_map: t.Dict[str, codeobject.Object] = {}

    seen: t.Set[str] = set()
    for name, spec in spec_map.items():
        if len(spec.arguments) > 0:
            code = create_component_code(spec, spec_map)
            code_map[name] = code

    def _visit(name: str) -> None:
        if name in seen:
            return
        seen.add(name)

        if name not in code_map:
            return

        spec = spec_map[name]
        for subname, _, _ in spec.arguments:
            if subname not in code_map:
                continue
            _visit(subname)

        code = code_map[name]
        m.stmt(code)

    # emit with dependencies ordered
    for name in spec_map:
        _visit(name)

    return m


def create_component_code(
    spec: fnspec.Fnspec, spec_map: t.Dict[str, fnspec.Fnspec]
) -> codeobject.Object:
    @codeobject.codeobject
    def _component_code(m: Module, name: str) -> Module:
        args = []
        for name, _, _ in spec.arguments:
            args.append(helpers._spec_to_arg_value__with_depends(spec_map[name]))

        with m.def_(
            spec.name,
            LazyArguments(args),
            return_type=f"{spec.module}.{_type_value(spec.return_type)}",
        ):
            # xxx: async
            is_coroutine = spec.is_coroutinefunction
            if is_coroutine:
                m.body.body[-3].fmt = f"async {m.body.body[-3].fmt}"

            m.return_(
                "{}({})",
                spec.fullname,
                LazyArguments([name for name, _, _ in spec.arguments]),
            )
            # xxx: await
            if is_coroutine:
                m.body.body[-2].fmt = m.body.body[-2].fmt.replace(
                    "return ", "return await "
                )
        return m

    _component_code.name == spec.name
    return _component_code