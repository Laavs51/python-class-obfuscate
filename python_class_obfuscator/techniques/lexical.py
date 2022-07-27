"""
Модуль для лексической обфускации кода
"""
from ast import *

from .utils import NamespaceObfuscator


class LexicalNamespaceObfuscator(NamespaceObfuscator):
    """ Лексический обфускатор кода """

    def visit_Expr(self, node):
        """ Удаляем комментарии """
        if isinstance(node.value, Constant):
            return None
        return self.generic_visit(node)

    def visit_Name(self, node):
        """ Рефакторинг переменных """
        node.id = self.alt_name(node.id)
        return self.generic_visit(node)

    def visit_keyword(self, node):
        """ Рефакторинг именованных параметров """
        node.arg = self.alt_name(node.arg)
        return self.generic_visit(node)

    def visit_Import(self, node):
        return self._convert_import(node)

    def visit_ImportFrom(self, node):
        return self._convert_import(node)

    def _convert_import(self, node):
        """ Импортирование под псевдонимом """
        for imported in node.names:
            imported.asname = self.alt_name(imported.asname or imported.name)
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        return self._convert_func(node)

    def visit_FunctionDef(self, node):
        return self._convert_func(node)

    def _convert_func(self, node):
        """ Рефакторинг имени функции и аргументов """
        name = node.name
        node.name = self.alt_name(name)

        for argument in node.args.args:
            argument.arg = self.alt_name(argument.arg)

        return self.generic_visit(node)
