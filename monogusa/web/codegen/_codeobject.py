from __future__ import annotations
from prestring.python import PythonModule
from prestring.codeobject import CodeObjectModuleMixin, codeobject, Object
from monogusa.langhelpers import reify


class Module(CodeObjectModuleMixin, PythonModule):
    @reify
    def toplevel(self) -> Module:
        return self.submodule()


__all__ = ["codeobject", "Module", "Object"]
