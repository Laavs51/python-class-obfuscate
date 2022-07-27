"""
Модуль для обфускации константных объектов
"""
from ast import *

from .utils import Obfuscator


class StringObfuscator(Obfuscator):
    """ Обфускатор строк """

    def visit_Expr(self, node):
        """ Расширенную документацию не трогаем, ее удалит лексический обфускатор """
        if isinstance(node.value, Constant) and isinstance(node.value.value, str):
            return node

        return self.generic_visit(node)

    def visit_Constant(self, node):
        """ Преобразуем константные строки в выражение-генератор этой строки """
        if isinstance(node.value, str) and node.value:
            node = self._encode_string(list(node.value))

        return self.generic_visit(node)

    def _encode_string(self, char_list):
        char = char_list.pop()
        chr_call = Call(
            func=Name(id='chr', ctx=Load()),
            args=[Constant(value=ord(char))],
            keywords=[]
        )

        if not bool(char_list):
            return chr_call

        return BinOp(
            left=self._encode_string(char_list),
            op=Add(),
            right=chr_call
        )
