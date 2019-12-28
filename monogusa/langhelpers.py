import typing as t
import inspect
from functools import update_wrapper


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
) -> t.Any:
    if inspect.iscoroutinefunction(action):
        return await action(*positionals, **keywords)
    else:
        return action(*positionals, **keywords)
