from __future__ import annotations
import typing as t
import typing_extensions as tx
import inspect
import dataclasses
from functools import update_wrapper
from monogusa.langhelpers import reify

# note: internal package, need to merge with metashape's one?


@dataclasses.dataclass
class Fnspec:
    body: t.Callable[..., t.Any]
    argspec: inspect.FullArgSpec
    _command_name: t.Optional[str] = None
    _module: t.Optional[str] = None
    _aliases: t.Dict[str, str] = dataclasses.field(
        default_factory=lambda: {"typing": "t"}  # xxx:
    )

    @property
    def command_name(self) -> str:
        return self._command_name or self.body.__name__

    @property
    def name(self) -> str:
        return self.body.__name__

    @property
    def module(self) -> str:
        m = self._module or self.body.__module__
        return self._aliases.get(m, m)

    @property
    def fullname(self) -> str:
        return f"{self.module}.{self.body.__name__}"

    @property
    def doc(self) -> t.Optional[str]:
        return self.body.__doc__

    @property
    def is_coroutinefunction(self) -> bool:
        return inspect.iscoroutinefunction(self.body)

    def kind_of(self, name: str) -> Kind:
        return self._classified[name]

    def default_of(self, name: str) -> t.Any:
        return self._defaults[name]

    def default_str_of(self, name: str) -> t.Any:
        val = self.default_of(name)
        return repr(val)

    def type_str_of(
        self, typ: t.Type[t.Any], *, nonetype: t.Type[t.Any] = type(None)
    ) -> str:
        if typ.__module__ == "builtins":
            if typ.__name__ == "NoneType":
                return "None"
            else:
                return typ.__name__

        if self.body.__module__ == typ.__module__:
            return f"{self.module}.{typ.__name__}"
        if hasattr(typ, "__name__"):
            return f"{self._aliases.get(typ.__module__, typ.__module__)}.{typ.__name__}"
        elif hasattr(typ, "__origin__"):  # for typing.Union, typing.Optional, ...
            prefix = self._aliases.get(typ.__module__, typ.__module__)
            args = typ.__args__
            if typ.__origin__ == t.Union and len(args) == 2:
                args = [x for x in args if x is not nonetype]
                if len(args) == 1:
                    return f"{prefix}.Optional[{self.type_str_of(args[0])}]"
            name = getattr(typ, "_name") or getattr(typ.__origin__, "_name")
            return f"{prefix}.{name}[{', '.join(self.type_str_of(x) for x in args)}]"
        return str(typ).replace(
            typ.__module__ + ".",
            self._aliases.get(typ.__module__, typ.__module__) + ".",
        )  # xxx

    @reify
    def parameters(self) -> t.List[t.Tuple[str, t.Type[t.Any], Kind]]:
        """arguments + keyword_arguments"""
        return [
            (name, v, self.kind_of(name))
            for name, v in self.argspec.annotations.items()
            if name != "return"
        ]

    @reify
    def return_type(self) -> t.Type[t.Any]:
        val = self.argspec.annotations["return"]  # type: t.Type[t.Any]
        return val

    @reify
    def arguments(self) -> t.List[t.Tuple[str, t.Type[t.Any], Kind]]:
        return [
            (name, v, kind)
            for name, v, kind in self.parameters
            if kind.startswith("arg")
        ]

    @reify
    def keyword_arguments(self) -> t.List[t.Tuple[str, t.Type[t.Any], Kind]]:
        return [
            (name, v, kind)
            for name, v, kind in self.parameters
            if kind.startswith("kw")
        ]

    @reify
    def _classified(self) -> t.Dict[str, Kind]:
        return _classify_args(self.argspec)

    @reify
    def _defaults(self) -> t.Dict[str, t.Any]:
        defaults = self.argspec.kwonlydefaults or {}
        if self.argspec.defaults:
            for val, name in zip(
                reversed(self.argspec.defaults), reversed(self.argspec.args)
            ):
                defaults[name] = val
        return defaults


def fnspec(fn: t.Callable[..., t.Any], *, name: t.Optional[str] = None) -> Fnspec:
    argspec = inspect.getfullargspec(fn)
    annotations = t.get_type_hints(fn)
    assert len(argspec.annotations) == len(annotations)
    argspec.annotations.update(annotations)
    spec = Fnspec(fn, argspec=argspec, _command_name=name)
    update_wrapper(spec, fn)  # type: ignore
    return spec


Kind = tx.Literal["args", "args_defaults", "kw", "kw_defaults", "var_args", "var_kw"]


def _classify_args(spec: inspect.FullArgSpec) -> t.Dict[str, Kind]:
    classified: t.Dict[str, Kind] = {}
    args_limit = len(spec.args or []) - len(spec.defaults or [])
    for i in range(args_limit):
        classified[spec.args[i]] = "args"
    for i in range(1, len(spec.defaults or []) + 1):
        classified[spec.args[-i]] = "args_defaults"
    for k in spec.kwonlyargs:
        classified[k] = "kw"
    for k in spec.kwonlydefaults or []:
        classified[k] = "kw_defaults"
    if spec.varkw:
        classified[spec.varkw] = "var_kw"
    if spec.varargs:
        classified[spec.varargs] = "var_args"
    return classified
