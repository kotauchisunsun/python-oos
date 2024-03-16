from class_definitions import Class, ClassConstructor
from attr_accessor import AttrType
from method_accessor import MethodType
from typing import List, Dict


class ClassManagement:
    classes: Dict[str, Class]

    def __init__(self) -> None:
        self.classes = {}

    def define(
        self,
        name: str,
        bases: List[Class],
        fields: List[AttrType],
        constructor: ClassConstructor,
        methods: Dict[str, MethodType] = {},
    ) -> None:
        self.classes[name] = Class(name, bases, fields, constructor, methods)

    def get_class(self, name: str) -> Class:
        return self.classes[name]
