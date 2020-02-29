from __future__ import annotations
import typing as t
import logging
import sys
import inspect
from types import ModuleType
from collections import ChainMap
from functools import partial
import dataclasses

from .langhelpers import run_with, run_with_async, fullname, get_origin_type

logger = logging.getLogger(__name__)
FunctionType = t.Callable[..., t.Any]


class Marker:
    pool: t.Dict[str, FunctionType]
    default_pool: t.Dict[t.Type[t.Any], FunctionType]

    def __init__(self, name: str) -> None:
        self.name = name
        self.pool = {}
        self.default_pool = {}

    def __call__(self, fn: FunctionType, *, default: bool = False) -> FunctionType:
        self.pool[fn.__name__] = fn
        setattr(fn, f"_marked_as_{self.name}", True)

        if default:
            argspec = _get_fullargspec(fn)
            ret_type = argspec.annotations.get("return")
            if ret_type is None:
                raise ValueError("please t.Callable[..., T]")
            self.default_pool[get_origin_type(ret_type)] = fn
        return fn

    def is_marked(self, fn: FunctionType) -> bool:
        v = getattr(fn, f"_marked_as_{self.name}", False)  # type: bool
        return v

    def __contains__(self, name: str) -> bool:
        return name in self.pool


class Pool:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pool: t.Dict[FunctionType, str] = {}

    def __call__(
        self, fn: FunctionType, *, name: t.Optional[str] = None,
    ) -> FunctionType:
        self.pool[fn] = name or fn.__name__
        return fn

    def __contains__(self, fn: FunctionType) -> bool:
        return fn in self.pool


def _get_fullargspec(fn: FunctionType) -> inspect.FullArgSpec:
    argspec = inspect.getfullargspec(fn)
    # XXX: for `from __future__ import annotations`
    annotations = t.get_type_hints(fn)
    assert len(argspec.annotations) == len(annotations)
    argspec.annotations.update(annotations)
    return argspec


Key = t.Tuple[t.Optional[str], t.Type[t.Any]]


class Resolver:
    def __init__(
        self,
        marker: Marker,
        once_marker: Marker,
        *,
        registry: t.Optional[t.Dict[Key, t.Any]] = None,
    ) -> None:
        self.marker = marker
        self.once_marker = once_marker

        if registry is None:
            registry = {}
        self.registry = registry

    def resolve_args(
        self,
        fn: t.Callable[..., t.Union[t.Awaitable[t.Any], t.Any]],
        *,
        i: int = 0,
        strict: bool = True,
    ) -> t.List[t.Any]:
        internal = _ResolverInternal(self)
        return internal.resolve_args(fn, i=i, strict=strict)

    async def resolve_args_async(
        self,
        fn: t.Callable[..., t.Union[t.Awaitable[t.Any], t.Any]],
        *,
        i: int = 0,
        strict: bool = True,
    ) -> t.List[t.Any]:
        internal = _ResolverInternal(self)
        return await internal.resolve_args_async(fn, i=i, strict=strict)


class _ResolverInternal:
    def __init__(self, resolver: Resolver) -> None:
        self.marker = resolver.marker
        self.once_marker = resolver.once_marker
        self.registry: t.MutableMapping[Key, t.Any] = ChainMap({}, resolver.registry)

        self.root_resolver = resolver

    def _type_check(self, val: t.Any, *, typ: t.Type[t.Any], strict: bool) -> None:
        if strict:
            if not hasattr(typ, "__origin__"):  # skip generics
                assert isinstance(val, typ), f"{val!r} is not instance of {typ!r}"

    def _lookup_component_factory(
        self, argspec: inspect.FullArgSpec, k: Key
    ) -> t.Optional[FunctionType]:
        name, typ = k
        if name is not None:
            factory = self.marker.pool.get(name)
            if factory is not None:
                logger.debug("component, got name=%s %r", name, fullname(typ))
                return factory
            factory = self.once_marker.pool.get(name)
            if factory is not None:
                logger.debug("once component, got name=%s %r", name, fullname(typ))
                return factory
            return None
        else:
            # default component
            logger.debug("default component, lookup %r", fullname(typ))
            factory = self.marker.default_pool.get(typ)
            if factory is not None:
                logger.debug("default component, got %r", fullname(typ))
                return factory
            factory = self.once_marker.default_pool.get(typ)
            if factory is not None:
                logger.debug("default once component, got %r", fullname(typ))
                return factory
            return None

    def resolve_args(
        self,
        fn: t.Callable[..., t.Union[t.Awaitable[t.Any], t.Any]],
        *,
        i: int = 0,
        strict: bool = True,
    ) -> t.List[t.Any]:
        argspec = _get_fullargspec(fn)

        g = self.marker.pool
        if not argspec.args and fn.__name__ in g:
            return []

        args = [None for i in range(i)] if i else []
        for name in argspec.args[i:]:
            typ = argspec.annotations[name]
            component_factory = None
            cached: t.Optional[t.Any] = None
            for k in [(name, typ), (None, typ)]:
                if k in self.registry:
                    cached = self.registry[k]
                    self._type_check(cached, typ=typ, strict=strict)
                    break

                component_factory = self._lookup_component_factory(argspec, k)
                if component_factory is not None:
                    break

            if cached is not None:
                args.append(cached)
                continue
            if component_factory is None:
                raise ValueError(f"component ({name} : {typ}) is not found")

            component_args = self.resolve_args(component_factory)
            val = run_with(component_factory, component_args, {})

            # global component?
            if self.once_marker.is_marked(component_factory):
                self.root_resolver.registry[k] = val
            else:
                self.registry[k] = val
            args.append(val)
            self._type_check(val, typ=argspec.annotations[name], strict=strict)

        return args

    async def resolve_args_async(
        self,
        fn: t.Callable[..., t.Union[t.Awaitable[t.Any], t.Any]],
        *,
        i: int = 0,
        strict: bool = True,
    ) -> t.List[t.Any]:
        argspec = _get_fullargspec(fn)

        g = self.marker.pool
        if not argspec.args and fn.__name__ in g:
            return []

        args = [None for i in range(i)] if i else []
        for name in argspec.args[i:]:
            typ = argspec.annotations[name]
            component_factory = None
            cached: t.Optional[t.Any] = None
            for k in [(name, typ), (None, typ)]:  # type: Key
                if k in self.registry:
                    cached = self.registry[k]
                    self._type_check(cached, typ=typ, strict=strict)
                    break

                component_factory = self._lookup_component_factory(argspec, k)
                if component_factory is not None:
                    break

            if cached is not None:
                args.append(cached)
                continue
            if component_factory is None:
                raise ValueError(f"component ({name} : {typ}) is not found")

            component_args = await self.resolve_args_async(component_factory)
            val = await run_with_async(component_factory, component_args, {})

            # global component?
            if self.once_marker.is_marked(component_factory):
                self.root_resolver.registry[k] = val
            else:
                self.registry[k] = val
            args.append(val)
            self._type_check(val, typ=argspec.annotations[name], strict=strict)

        return args


component = Marker("component")
default_component = partial(component, default=True)
is_component = component.is_marked
once = Marker("once")
default_once = partial(once, default=True)
is_once = once.is_marked
ignore = Marker("ignore")
is_ignored = ignore.is_marked
only = Marker("only")
is_only = only.is_marked
global_registry: t.Dict[Key, t.Any] = {}

export_as_command = Pool("exported_commands")


def get_component_marker() -> Marker:
    global component
    return component


def get_once_marker() -> Marker:
    global once
    return once


def get_ignore_marker() -> Marker:
    global ignore
    return ignore


def get_resolver(registry: t.Optional[t.Dict[Key, t.Any]] = None) -> Resolver:
    global global_registry
    if registry is None:
        registry = global_registry

    return Resolver(
        marker=get_component_marker(), once_marker=get_once_marker(), registry=registry,
    )


def resolve_args(fn: FunctionType, *, i: int = 0) -> t.List[t.Any]:
    return get_resolver().resolve_args(fn, i=i)


async def resolve_args_async(fn: FunctionType, *, i: int = 0) -> t.List[t.Any]:
    return await get_resolver().resolve_args_async(fn, i=i)


def scan_module(
    module: t.Optional[ModuleType] = None,
    where: t.Optional[str] = None,
    *,
    ignore_only: bool = False,
    _depth: int = 1,
    _is_ignored: t.Callable[[FunctionType], bool] = is_ignored,
    _is_component: t.Callable[[FunctionType], bool] = is_component,
    _is_only: t.Callable[[FunctionType], bool] = is_only,
) -> Scanned:
    if module is not None:
        _globals = module.__dict__
    else:
        frame = sys._getframe(_depth)  # black magic
        _globals = frame.f_globals
    where = _globals["__name__"]

    commands = []
    only_commands = []
    components = []

    for name, v in _globals.items():
        if name.startswith("_"):
            continue

        if _is_ignored(v):
            logger.debug("%r is ignored, skipped", fullname(v))
            continue

        if _is_component(v):
            components.append(v)
        elif inspect.isfunction(v) and (
            v.__module__ == where or v in export_as_command
        ):
            if _is_only(v) and not ignore_only:
                logger.debug("only, name=%r %r", name, v)
                only_commands.append(v)
            commands.append(v)

    return Scanned(commands=only_commands or commands, components=components)


@dataclasses.dataclass(frozen=True)
class Scanned:
    commands: t.List[FunctionType]
    components: t.List[FunctionType]


def get_command_name(fn: FunctionType, *, _pool: Pool = export_as_command) -> str:
    return _pool.pool.get(fn) or fn.__name__
