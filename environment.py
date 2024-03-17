from typing import Any
from attr_accessor import AttrType
from class_definitions import ClassConstructor, MessageType
from class_management import ClassManagement
from instance import Instance
from instance_management import InstanceManagement
from method_accessor import MethodType


class Environment:
    def __init__(self) -> None:
        self.class_definitions = ClassManagement()
        self.instance_management = InstanceManagement()

    def define(
        self,
        name: str,
        bases: list[str],
        attrs: list[AttrType],
        constructor: ClassConstructor,
        methods: dict[str, MethodType],
    ) -> None:
        base_classes = [self.class_definitions.get_class(base) for base in bases]
        self.class_definitions.define(name, base_classes, attrs, constructor, methods)

    def new(self, cls: str, name: str, **argv: MessageType) -> Any:
        _class = self.class_definitions.get_class(cls)
        instance = self.instance_management.make_instance(_class, name)
        return instance

    def get_instance(self, instance_name: str) -> Instance:
        return self.instance_management.get_instance(instance_name)

    def register_instance(self, name: str, instance: Instance) -> None:
        self.instance_management.register_instance(name, instance)

    def __enter__(self) -> None:
        self.instance_management.push()

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.instance_management.pop()
