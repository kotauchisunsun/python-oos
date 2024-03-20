import random
from typing import Any
from attr_accessor import AttrType, PublicAttr
from class_definitions import ClassConstructor, MessageType
from class_management import ClassManagement
from instance import Instance
from instance_management import InstanceManagement
from method_accessor import MethodType, PublicMethod


class Environment:
    def __init__(self) -> None:
        self.class_definitions = ClassManagement()
        self.instance_management = InstanceManagement()

        self.define(
            "int",
            [],
            [PublicAttr("value")],
            lambda sys: sys.send(
                "this", "set-value", value=sys.send("args", "get-value")
            ),
            {
                "add": PublicMethod(
                    lambda sys: self.new_int(
                        "int_%f" % random.random(),
                        sys.send("this", "get-value")
                        + sys.send(sys.send("args", "get-value"), "get-value"),
                    )
                ),
                "sub": PublicMethod(
                    lambda sys: self.new_int(
                        "int_%f" % random.random(),
                        sys.send("this", "get-value")
                        - sys.send(sys.send("args", "get-value"), "get-value"),
                    )
                ),
                "multiply": PublicMethod(
                    lambda sys: self.new_int(
                        "int_%f" % random.random(),
                        sys.send("this", "get-value")
                        * sys.send(sys.send("args", "get-value"), "get-value"),
                    )
                ),
                "max": PublicMethod(
                    lambda sys: self.new_int(
                        "int_%f" % random.random(),
                        max(
                            sys.send("this", "get-value"),
                            sys.send(sys.send("args", "get-value"), "get-value"),
                        ),
                    )
                ),
            },
        )

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

    def new(self, cls: str, name: str) -> Any:
        _class = self.class_definitions.get_class(cls)
        instance = self.instance_management.make_instance(_class, name)
        return instance

    def new_int(self, name: str, value: int) -> Instance:
        instance = self.new("int", name)
        instance.attributes["value"] = value
        return instance

    def get_instance(self, instance_name: str) -> Instance:
        return self.instance_management.get_instance(instance_name)

    def register_instance(self, name: str, instance: Instance) -> None:
        self.instance_management.register_instance(name, instance)

    def __enter__(self) -> None:
        self.instance_management.push()

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.instance_management.pop()
