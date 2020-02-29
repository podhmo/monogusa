import typing as t
import sys
import re
import pathlib

from ._codeobject import Module
from . import _fnspec as fnspec


def setup_module(*, header: t.Optional[str] = None) -> Module:
    m = Module(import_unique=True)

    m.toplevel  # create
    m.sep()

    if header:
        m.toplevel.stmt(header)
    return m


def emit_target_spec_import(spec: fnspec.Fnspec, *, where: str, m: Module) -> str:
    parent_dir = str(pathlib.Path(sys.modules[spec.module].__file__).parent.absolute())
    if _is_valid_module_name(spec.module) and where == parent_dir:
        m.toplevel.import_(spec.module)
        return spec.module

    m.toplevel.import_("magicalimport")
    valid_modname = _to_valid_module_name(spec.module)
    target_file_path = sys.modules[spec.module].__file__
    m.stmt(
        "{} = magicalimport.import_module({!r}, cwd=True)",
        valid_modname,
        target_file_path,
    )
    m.sep()
    return valid_modname


def _is_valid_module_name(
    name: str, *, _rx: t.Pattern[str] = re.compile(r"^[_a-zA-Z][_a-zA-Z0-9]+$")
) -> bool:
    return _rx.match(name) is not None


def _to_valid_module_name(
    name: str, *, _ignore_rx: t.Pattern[str] = re.compile("[^0-9a-zA-Z_]+")
) -> str:
    c = name[0]
    if c.isdigit():
        name = "n" + name
    elif not (c.isalpha() or c == "_"):
        name = "x" + name
    return _ignore_rx.sub("_", name.replace("-", "_"))


def _spec_to_arg_value__with_depends(spec: fnspec.Fnspec) -> str:
    if len(spec.arguments) == 0:
        return f"{spec.name}: {spec.type_str_of(spec.return_type)}=Depends({spec.fullname})"

    return f"{spec.name}: {spec.type_str_of(spec.return_type)}=Depends({spec.name})"
