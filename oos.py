from dataclasses import dataclass
from method_accessor import PublicMethod, PrivateMethod, MethodType
from attr_accessor import AttrType
from class_management import ClassManagement
from instance import Instance
from instance_management import InstanceManagement
from exceptions import MethodAccessDenied
from typing import List, Dict, Any
from class_definitions import MessageType, ClassConstructor


class InternalObjectOrientedSystem:
    class_definitions: ClassManagement
    instance_management: InstanceManagement

    def __init__(self) -> None:
        self.class_definitions = ClassManagement()
        self.instance_management = InstanceManagement()

    def def_class(
        self,
        name: str,
        bases: List[str],
        fields: List[AttrType],
        constructor: ClassConstructor,
        methods: Dict[str, MethodType] = {},
    ) -> None:
        _bases = [self.class_definitions.get_class(base) for base in bases]
        self.class_definitions.define(name, _bases, fields, constructor, methods)

    def make_instance(
        self, class_name: str, instance_name: str, **argv: MessageType
    ) -> Instance:
        _class = self.class_definitions.get_class(class_name)
        instance = self.instance_management.make_instance(_class, instance_name)
        _class.constructor(self, instance, **argv)
        return instance

    def send_to(self, instance_name: str, method: str, **argv: MessageType) -> Any:
        instance = self.instance_management.get_instance(instance_name)

        f = instance.class_type.get_method(method)
        if isinstance(f, PrivateMethod):
            raise MethodAccessDenied(f"{method} is PrivateMethod")
        elif isinstance(f, PublicMethod):
            return self.call(instance, method, **argv)

    def call(self, instance: Instance, method: str, **argv: MessageType) -> Any:
        f = instance.class_type.get_method(method)
        return f.method(self, instance, **argv)


class ObjectOrientedSystem:
    sys: InternalObjectOrientedSystem

    def __init__(self) -> None:
        self.sys = InternalObjectOrientedSystem()

    def def_class(
        self,
        name: str,
        bases: List[str],
        fields: List[AttrType],
        constructor: ClassConstructor = lambda sys, this, **args: None,
        methods: Dict[str, MethodType] = {},
    ) -> None:
        self.sys.def_class(name, bases, fields, constructor, methods)

    def make_instance(
        self, class_name: str, instance_name: str, **argv: MessageType
    ) -> Instance:
        return self.sys.make_instance(class_name, instance_name, **argv)

    def send_to(self, instance_name: str, method: str, **argv: MessageType) -> Any:
        return self.sys.send_to(instance_name, method, **argv)
