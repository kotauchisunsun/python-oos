from typing import Sequence
from class_definitions import Class,ClassInterface, ClassConstructor
from attr_accessor import AttrType
from method_accessor import MethodType


class ClassManagement:
    classes: dict[str, Class]

    def __init__(self) -> None:
        self.classes = {}

    def define(
        self,
        name: str,
        bases: Sequence[ClassInterface],
        fields: list[AttrType],
        constructor: ClassConstructor,
        methods: dict[str, MethodType] = {},
    ) -> None:
        self.classes[name] = Class(name, bases, fields, constructor, methods)

    def get_class(self, name: str) -> Class:
        return self.classes[name]
