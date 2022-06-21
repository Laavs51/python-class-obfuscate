"""
Пакет с модулями, предназначенными для обфускации ast представлений кода
"""
import ast

from attr_writer import AttrObfuscator
from class_to_dynamic_type import ClassObfuscator
from lexical import LexicalNamespaceObfuscator
from string_as_predicate import StringObfuscator


def obfuscate(code):
    """
    Алгоритм обфускации:
    1. Реструктуризация объявлений классов в динамический тип
    2. Смена обычных манипуляций атрибутов на операции в getattr и setattr
    3. Преобразование константных строк в процедурно генерируемые
    4. Лексическая обфускация кода
    """
    tree = ast.parse(code)

    for technique in [ClassObfuscator, AttrObfuscator, StringObfuscator, LexicalNamespaceObfuscator]:
        tree = technique().obfuscate(tree)

        # После преобразований положения узлов могут сбиваться или отсутствовать.
        # Такое поведение может вызвать ошибки и их тяжело рассчитать заново.
        # Принудительная перезагрузка дерева решает эту проблему ценой производительности.
        ast.fix_missing_locations(tree)
        code = ast.unparse(tree)
        tree = ast.parse(code)

    return ast.unparse(tree)
