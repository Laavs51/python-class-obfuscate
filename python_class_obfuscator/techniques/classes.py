from ast import *

from .utils import NamespaceObfuscator


class ClassObfuscator(NamespaceObfuscator):
    """ Обфускатор классов """

    def visit_ClassDef(self, node):
        transformed = []

        for item in ClassTransformer(node, self.names).obfuscate(node):
            item_transformed = self.visit(item)
            if isinstance(item_transformed, list):
                transformed.extend(item_transformed)
            else:
                transformed.append(item_transformed)
        return transformed


class ClassTransformer(NamespaceObfuscator):
    """ Трансформатор класса в динамический тип """

    def __init__(self, root, names=None):
        super().__init__(names)
        self.root = root
        self.instance_name = None

    def visit_FunctionDef(self, node):
        """ Сохранение первого аргумента из последней пройденной функции """
        self.instance_name = node.args.args[0].arg
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_Call(self, node):
        """ Трансформация вызова функции """
        if isinstance(node.func, Name) and node.func.id == 'super' and not node.args:
            # Особенность функции super() в том, что интерпретатор сам подставляет в нее аргументы.
            # Поэтому она не будет работать без аргументов вне стандартного объявления.
            # В связи с этим придется самим подставить аргументы вместо интерпретатора.
            class_name = Name(id=self.root.name, ctx=Load())
            instance_name = Name(self.instance_name, ctx=Load())
            node.args = [class_name, instance_name]

        return self.generic_visit(node)

    def visit_ClassDef(self, node):
        """ Трансформация объявления класса в динамический тип """
        if id(node) != id(self.root):
            # Объявления классов, отличные от корневого,
            # будут трансформированы отдельным вызовом
            return node

        attr_map = self._attr_map(node.body)
        dynamic_type = self._dynamic_type(node, attr_map)
        transformed_body = self._dynamic_type_def(node, dynamic_type)

        return map(self.visit, transformed_body)

    def _attr_map(self, attributes):
        """ Список атрибутов для динамического типа """
        attr_map = {}

        for attr in attributes:
            if isinstance(attr, Assign):
                target = attr.targets[0]
                key = Constant(value=target.id)

                target.id = self.resolve_conflict(target.id)
                attr_map[key] = target
            elif isinstance(attr, (FunctionDef, AsyncFunctionDef, ClassDef)):
                key = Constant(value=attr.name)

                attr.name = self.resolve_conflict(attr.name)
                func_as_name = Name(id=attr.name, ctx=Load())
                attr_map[key] = self._wrap_decors(func_as_name, attr)

        return attr_map

    def _dynamic_type(self, class_node, attributes):
        """ Создать динамический тип из информации о преобразуемом классе """
        type_func = Call(
            func=Name(id='type', ctx=Load()),
            args=[
                Constant(value=class_node.name),
                Tuple(elts=class_node.bases, ctx=Load()),
                Dict(
                    keys=attributes.keys(),
                    values=attributes.values()
                )
            ],
            keywords=[]
        )

        return self._wrap_decors(type_func, class_node)

    def _dynamic_type_def(self, func, type_func_call):
        """ Итоговое формирование списка объектов на замену обычного класса """
        assign = Assign(
            targets=[Name(id=self.root.name, ctx=Store())],
            value=type_func_call
        )

        return func.body + [assign]

    def _wrap_decors(self, obj, node):
        """ Заменить список декораторов у узла на обернутый вызов из этих декораторов """
        transformed = obj

        for decorator in reversed(node.decorator_list):
            transformed = Call(
                func=Name(id=decorator.id, ctx=Load()),
                args=[transformed],
                keywords=[]
            )

        node.decorator_list = []

        return transformed
