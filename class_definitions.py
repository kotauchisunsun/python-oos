from dataclasses import dataclass
from method_accessor import PublicMethod, PrivateMethod, MethodType
from attr_accessor import PublicAttr, PrivateAttr, ReadonlyAttr, AttrType
from exceptions import MethodNotFound
from typing import Callable, List, Dict, Iterable, Any, Callable

MessageType = Any


def build_getter_setter(attr: AttrType) -> tuple[MethodType, MethodType]:
    from oos import ObjectOrientedSystem as System

    attr_name = attr.name

    def getter(sys: System, **args: Dict[str, Any]) -> Any:
        return sys.instance_management.get_instance("this").attributes[attr_name]

    def setter(sys: System, **args: Dict[str, Any]) -> None:
        sys.instance_management.get_instance("this").attributes[attr_name] = args[
            "value"
        ]

    GetterMethodClass, SetterMethodClass = {
        PublicAttr: (PublicMethod, PublicMethod),
        PrivateAttr: (PrivateMethod, PrivateMethod),
        ReadonlyAttr: (PublicMethod, PrivateMethod),
    }[type(attr)]

    return GetterMethodClass(getter), SetterMethodClass(setter)


ClassConstructor = Callable[..., None]


@dataclass
class Class:
    name: str
    bases: List[Any]
    attrs: List[AttrType]
    constructor: ClassConstructor
    methods: Dict[str, MethodType]

    def get_default_attr(self) -> Dict[str, AttrType]:
        attrs = {}
        for f in self.attrs:
            attrs[f.name] = f.value
        for base in self.bases:
            attrs.update(base.get_default_attr())
        return attrs

    def find_method(self, name: str) -> Iterable[MethodType]:
        if name in self.methods:
            yield self.methods[name]
            return
        for base in self.bases:
            for f in base.find_method(name):
                yield f
                return

    def get_method(self, name: str) -> MethodType:
        for f in self.find_method(name):
            return f
        raise MethodNotFound(f"{name} not found")
