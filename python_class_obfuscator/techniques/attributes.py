"""
Модуль для преобразования атрибутов объектов
"""
from ast import *

from .utils import Obfuscator


class AttrObfuscator(Obfuscator):
    """ Обфускация атрибутов """

    def visit_Assign(self, node):
        """ Смена установки значения атрибута на вызов setattr """
        attr = node.targets[0]

        if isinstance(attr, Attribute):
            node = Expr(value=Call(
                func=Name(id='setattr', ctx=Load()),
                args=[
                    attr.value,
                    Constant(value=attr.attr),
                    node.value
                ],
                keywords=[]
            ))

        return self.generic_visit(node)

    def visit_Attribute(self, node):
        """ Смена получения значения атрибута на вызов getattr """
        node = Call(
            func=Name(id='getattr', ctx=Load()),
            args=[
                node.value,
                Constant(value=node.attr)
            ],
            keywords=[]
        )

        return self.generic_visit(node)
