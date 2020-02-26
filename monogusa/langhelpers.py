import typing as t
import inspect
import logging
from functools import update_wrapper, partial
import magicalimport

if t.TYPE_CHECKING:
    import asyncio


magicalimport.logger.setLevel(logging.INFO)
import_module = magicalimport.import_module
T = t.TypeVar("T")


# stolen from pyramid
class reify(t.Generic[T]):
    """cached property"""

    def __init__(self, wrapped: t.Callable[[t.Any], T]):
        self.wrapped = wrapped
        update_wrapper(self, wrapped)  # type: ignore

    def __get__(
        self, inst: t.Optional[object], objtype: t.Optional[t.Type[t.Any]] = None
    ) -> T:
        if inst is None:
            return self  # type: ignore
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


def run_with(
    action: t.Callable[..., t.Union[t.Any, t.Awaitable[t.Any]]],
    positionals: t.Sequence[t.Any],
    keywords: t.Mapping[str, t.Any],
    *,
    debug: bool = False,
) -> t.Any:
    if inspect.iscoroutinefunction(action):
        import asyncio

        return asyncio.run(action(*positionals, **keywords), debug=debug)
    else:
        return action(*positionals, **keywords)


async def run_with_async(
    action: t.Callable[..., t.Union[t.Any, t.Awaitable[t.Any]]],
    positionals: t.Sequence[t.Any],
    keywords: t.Mapping[str, t.Any],
    *,
    debug: bool = False,
    loop: "t.Optional[asyncio.AbstractEventLoop]" = None,
) -> t.Any:
    if inspect.iscoroutinefunction(action):
        return await action(*positionals, **keywords)
    else:
        import asyncio

        loop = loop or asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, partial(action, *positionals, **keywords)
        )


def fullname(typ: t.Type[t.Any]) -> str:
    return f"{typ.__module__}.{typ.__name__}"


def get_origin_type(typ: t.Type[t.Any]) -> t.Type[t.Any]:
    if hasattr(typ, "__origin__"):
        return typ.__origin__
    return typ
