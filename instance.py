from attr_accessor import AttrType, PrivateAttr, PublicAttr, ReadonlyAttr
from class_definitions import Class, ClassInterface
from typing import Any, Iterable
from exceptions import MethodNotFound
from method_accessor import MethodType, PrivateMethod, PublicMethod


class Instance:
    def __init__(self, class_type: Class, attributes: dict[str, Any]) -> None:
        self.class_type = class_type
        self.attributes = attributes

    def get_method(self, name: str) -> Any:
        for f in self.class_type.find_method(name):
            return f
        for f in find_attr_functions(self, self.class_type, name):
            return f
        raise MethodNotFound(name)

    @staticmethod
    def new_from_class(class_type: Class) -> "Instance":
        return Instance(class_type, class_type.get_default_attr())


def find_attr_functions(
    instance: Instance, class_type: ClassInterface, name: str
) -> Iterable[MethodType]:
    for attr in class_type.attrs:
        getter, setter = build_getter_setter(instance, attr)
        getter_name = f"get-{attr.name}"
        setter_name = f"set-{attr.name}"
        if name == getter_name:
            yield getter
            return
        elif name == setter_name:
            yield setter
            return
    for base in class_type.bases:
        for f in find_attr_functions(instance, base, name):
            yield f
            return


def build_getter_setter(
    this: Instance, attr: AttrType
) -> tuple[MethodType, MethodType]:
    from oos import ObjectOrientedSystem as System

    def getter(sys: System) -> Any:
        return this.attributes[attr.name]

    def setter(sys: System) -> None:
        this.attributes[attr.name] = sys.send("args", "get-value")

    table: dict[type[AttrType], tuple[type[MethodType], type[MethodType]]] = {
        PublicAttr: (PublicMethod, PublicMethod),
        PrivateAttr: (PrivateMethod, PrivateMethod),
        ReadonlyAttr: (PublicMethod, PrivateMethod),
    }

    GetterMethodClass, SetterMethodClass = table[type(attr)]

    return GetterMethodClass(getter), SetterMethodClass(setter)
