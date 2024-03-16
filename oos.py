from method_accessor import PublicMethod, PrivateMethod, MethodType
from attr_accessor import AttrType
from class_management import ClassManagement
from instance import Instance
from instance_management import InstanceManagement
from exceptions import MethodAccessDenied
from typing import Any
from class_definitions import MessageType, ClassConstructor


class ObjectOrientedSystem:
    class_definitions: ClassManagement
    instance_management: InstanceManagement

    def __init__(self) -> None:
        self.class_definitions = ClassManagement()
        self.instance_management = InstanceManagement()

    def def_class(
        self,
        name: str,
        bases: list[str],
        fields: list[AttrType],
        constructor: ClassConstructor = lambda sys, **args: None,
        methods: dict[str, MethodType] = {},
    ) -> None:
        base_classes = [self.class_definitions.get_class(base) for base in bases]
        self.class_definitions.define(name, base_classes, fields, constructor, methods)

    def make_instance(
        self, class_name: str, instance_name: str, **argv: MessageType
    ) -> Instance:
        _class = self.class_definitions.get_class(class_name)
        instance = self.instance_management.make_instance(_class, instance_name)
        with self.instance_management:
            self.instance_management.register_instance("this", instance)
            _class.constructor(self, **argv)
        return instance

    def send(self, instance_name: str, method: str, **argv: MessageType) -> Any:
        instance = self.instance_management.get_instance(instance_name)

        f = instance.get_method(method)

        with self.instance_management:
            self.instance_management.register_instance("this", instance)
            if instance_name == "this":
                return self.__call(instance, method, **argv)

            if isinstance(f, PrivateMethod):
                raise MethodAccessDenied(f"{method} is PrivateMethod")
            elif isinstance(f, PublicMethod):
                return self.__call(instance, method, **argv)

    def __call(self, instance: Instance, method: str, **argv: MessageType) -> Any:
        f = instance.get_method(method)
        return f.method(self, **argv)
