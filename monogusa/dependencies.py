from __future__ import annotations
import typing as t
import logging
import sys
import inspect
from types import ModuleType
from collections import ChainMap
from functools import partial
import dataclasses

from .langhelpers import run_with, run_with_async

logger = logging.getLogger(__name__)


class Marker:
    pool: t.Dict[str, t.Callable[..., t.Any]]
    default_pool: t.Dict[t.Type[t.Any], t.Callable[..., t.Any]]

    def __init__(self, name: str) -> None:
        self.name = name
        self.pool = {}
        self.default_pool = {}

    def __call__(
        self, fn: t.Callable[..., t.Any], *, default: bool = False
    ) -> t.Callable[..., t.Any]:
        self.pool[fn.__name__] = fn
        setattr(fn, f"_marked_as_{self.name}", True)

        if default:
            ret_type = _get_fullargspec(fn).annotations.get("return")
            if ret_type is None:
                raise ValueError("please t.Callable[..., T]")
            self.default_pool[ret_type] = fn
        return fn

    def is_marked(self, fn: t.Callable[..., t.Any]) -> bool:
        v = getattr(fn, f"_marked_as_{self.name}", False)  # type: bool
        return v

    def __contains__(self, name: str) -> bool:
        return name in self.pool


def _get_fullargspec(fn: t.Callable[..., t.Any]) -> inspect.FullArgSpec:
    argspec = inspect.getfullargspec(fn)
    # XXX: for `from __future__ import annotations`
    annotations = t.get_type_hints(fn)
    assert len(argspec.annotations) == len(annotations)
    argspec.annotations.update(annotations)
    return argspec


class Resolver:
    def __init__(self, marker: Marker, once_marker: Marker) -> None:
        self.marker = marker
        self.once_marker = once_marker
        self.registry: t.Dict[str, t.Any] = {}

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
        self.registry: t.MutableMapping[str, t.Any] = ChainMap({}, resolver.registry)

        self.root_resolver = resolver

    def _type_check(self, val: t.Any, *, typ: t.Type[t.Any], strict: bool) -> None:
        if strict:
            if not hasattr(typ, "__origin__"):  # skip generics
                assert isinstance(val, typ), f"{val!r} is not instance of {typ!r}"

    def _lookup_component_factory(
        self, argspec: inspect.FullArgSpec, name: str
    ) -> t.Callable[..., t.Any]:
        factory = self.marker.pool.get(name)
        if factory is not None:
            return factory

        typ = argspec.annotations.get(name)
        if typ is None:
            raise ValueError(
                f"component ({name} : {argspec.annotations.get(name)}) is not found"
            )

        logger.debug("lookup default component, type=%r", typ)
        factory = self.marker.default_pool.get(typ)
        if factory is not None:
            return factory

        factory = self.once_marker.default_pool.get(typ)
        if factory is not None:
            return factory

        raise ValueError(
            f"component ({name} : {argspec.annotations.get(name)}) is not found"
        )

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
            if name in self.registry:
                val = self.registry[name]
                args.append(val)
                self._type_check(val, typ=argspec.annotations[name], strict=strict)
                continue

            component_factory = self._lookup_component_factory(argspec, name)
            component_args = self.resolve_args(component_factory)
            val = run_with(component_factory, component_args, {})

            # global compnent?
            if self.once_marker.is_marked(component_factory):
                self.root_resolver.registry[name] = val
            else:
                self.registry[name] = val
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

        if not argspec.args and fn.__name__ in self.marker.pool:
            return []

        args = [None for i in range(i)] if i else []
        for name in argspec.args[i:]:
            if name in self.registry:
                val = self.registry[name]
                args.append(val)
                self._type_check(val, typ=argspec.annotations[name], strict=strict)
                continue

            component_factory = self._lookup_component_factory(argspec, name)
            component_args = await self.resolve_args_async(component_factory)
            val = await run_with_async(component_factory, component_args, {})

            # global component?
            if self.once_marker.is_marked(component_factory):
                self.root_resolver.registry[name] = val
            else:
                self.registry[name] = val
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


def get_component_marker() -> Marker:
    global component
    return component


def get_once_marker() -> Marker:
    global once
    return once


def get_ignore_marker() -> Marker:
    global ignore
    return ignore


def get_resolver() -> Resolver:
    return Resolver(marker=get_component_marker(), once_marker=get_once_marker())


def resolve_args(fn: t.Callable[..., t.Any], *, i: int = 0) -> t.List[t.Any]:
    return get_resolver().resolve_args(fn, i=i)


async def resolve_args_async(
    fn: t.Callable[..., t.Any], *, i: int = 0
) -> t.List[t.Any]:
    return await get_resolver().resolve_args_async(fn, i=i)


def scan_module(
    module: t.Optional[ModuleType] = None,
    where: t.Optional[str] = None,
    _depth: int = 1,
    ignore_only: bool = False,
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
            logger.debug("skip, name=%r is ignored", name)
            continue
        if is_ignored(v):
            logger.debug("skip, name=%r %r is ignored", name, v)
            continue
        if is_component(v):
            components.append(v)
        elif inspect.isfunction(v) and v.__module__ == where:
            if is_only(v) and not ignore_only:
                logger.debug("only, name=%r %r", name, v)
                only_commands.append(v)
            commands.append(v)

    return Scanned(commands=only_commands or commands, components=components)


@dataclasses.dataclass(frozen=True)
class Scanned:
    commands: t.List[t.Callable[..., t.Any]]
    components: t.List[t.Callable[..., t.Any]]
