import dataclasses
import random

random.seed(42)


@dataclasses.dataclass
class A:
    n: float = dataclasses.field(default_factory=random.random)


@dataclasses.dataclass
class B:
    a: A
    n: float = dataclasses.field(default_factory=random.random)


@dataclasses.dataclass
class C:
    a: A
    n: float = dataclasses.field(default_factory=random.random)


def test_prepare():
    a = A()
    assert a == a
    assert a != A()
    assert B(a=a) != B(a=a)
    assert B(a=a) != C(a=a)


def test_normal():
    from monogusa.dependencies import Marker
    from monogusa.dependencies import Resolver
    from collections import defaultdict

    called_count = defaultdict(int)
    marker = Marker("_marker")

    @marker
    def a() -> A:
        called_count[a.__name__] += 1
        return A()

    @marker
    def b(a: A) -> B:
        called_count[b.__name__] += 1
        return B(a=a)

    @marker
    def c(a: A) -> C:
        called_count[c.__name__] += 1
        return C(a=a)

    def use(b: B, c: C) -> None:
        called_count[use.__name__] += 1

    resolver = Resolver(marker, once_marker=Marker("once_marker"))
    args1 = resolver.resolve_args(use, strict=True)

    assert len(args1) == 2
    assert isinstance(args1[0], B)
    assert isinstance(args1[1], C)
    assert args1[0].a == args1[1].a

    assert called_count == {"a": 1, "b": 1, "c": 1}

    # second time
    args2 = resolver.resolve_args(use, strict=True)
    assert isinstance(args2[0], B)
    assert args2[0] != args1[0]
    assert isinstance(args2[1], C)
    assert args2[1] != args1[1]
    assert called_count == {"a": 2, "b": 2, "c": 2}


def test_for_global_component():
    # once + component = global component

    from monogusa.dependencies import Marker
    from monogusa.dependencies import Resolver
    from collections import defaultdict

    called_count = defaultdict(int)
    marker = Marker("_marker")
    once_marker = Marker("_once_marker")

    @marker
    @once_marker
    def a() -> A:
        called_count[a.__name__] += 1
        return A()

    @marker
    @once_marker
    def b(a: A) -> B:
        called_count[b.__name__] += 1
        return B(a=a)

    @marker
    def c(a: A) -> C:
        called_count[c.__name__] += 1
        return C(a=a)

    def use(b: B, c: C) -> None:
        called_count[use.__name__] += 1

    resolver = Resolver(marker, once_marker=once_marker)
    args1 = resolver.resolve_args(use, strict=True)

    assert len(args1) == 2
    assert isinstance(args1[0], B)
    assert isinstance(args1[1], C)
    assert args1[0].a == args1[1].a

    assert called_count == {"a": 1, "b": 1, "c": 1}

    # second time
    args2 = resolver.resolve_args(use, strict=True)

    assert isinstance(args2[0], B)
    assert args2[0] == args1[0]
    assert isinstance(args2[1], C)
    assert args2[1] != args1[1]

    assert called_count == {"a": 1, "b": 1, "c": 2}
