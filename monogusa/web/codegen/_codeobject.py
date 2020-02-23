from prestring.python import PythonModule
from prestring.codeobject import CodeObjectModuleMixin, codeobject, Object


class Module(PythonModule, CodeObjectModuleMixin):
    pass


__all__ = ["codeobject", "Module", "Object"]
