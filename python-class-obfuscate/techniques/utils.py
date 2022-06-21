"""
Модуль со вспомогательными функциями и объектами
"""
import builtins
from ast import NodeTransformer, NodeVisitor
from functools import lru_cache


class Obfuscator(NodeTransformer):
    """ Базовый класс обфускатора """

    def obfuscate(self, tree):
        """ Запуск процесса обфускации """
        return self.visit(tree)


class NamespaceObfuscator(Obfuscator):
    """ Базовый класс обфускатора, предполагающий разрешение конфликтов в пространстве имен """

    class NamesCollector(NodeVisitor):
        """ Сборщик идентификаторов со всего дерева """

        def __init__(self):
            super().__init__()
            self.names = set()

        def collect(self, tree):
            self.visit(tree)
            return self.names

        def visit_Name(self, node):
            self.names.add(node.id)
            self.generic_visit(node)

        def visit_ClassDef(self, node):
            self.names.add(node.name)
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            self.visit_ClassDef(node)

        def visit_AsyncFunctionDef(self, node):
            self.visit_ClassDef(node)

    def __init__(self, names=None):
        super().__init__()
        if not names:
            names = set()
        self.names = names

    def obfuscate(self, tree):
        if not self.names:
            self.names = self.NamesCollector().collect(tree)

        return super().obfuscate(tree)

    @lru_cache
    def alt_name(self, name):
        """ Получить незначащее имя на замену """
        if name not in builtins_list():
            new_name = self.resolve_conflict('_')
        else:
            new_name = name

        return new_name

    def resolve_conflict(self, name):
        """ Возвращает уникальное новое имя на основе переданного """
        new_name = name
        if name not in builtins_list():
            while new_name in self.names:
                new_name += '_'

        self.names.add(new_name)
        return new_name


@lru_cache
def builtins_list():
    """ Список встроенных функций """
    return dir(builtins)
