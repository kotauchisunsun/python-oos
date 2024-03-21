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

        self.primitive_types = [int, float]

        for t in self.primitive_types:
            define_primitive(self, t)

    def is_primitive(self, value: Any) -> bool:
        return any(isinstance(value, t) for t in self.primitive_types)

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

    def new(self, cls: str, name: str) -> Instance:
        _class = self.class_definitions.get_class(cls)
        instance = self.instance_management.make_instance(_class, name)
        return instance

    def new_tmp_primitive(self, value: Any) -> Instance:
        cls = self.class_definitions.get_class(type(value).__name__)
        instance = Instance.new_from_class(cls)
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


def define_primitive(env: Environment, cls: type) -> None:
    env.define(
        cls.__name__,
        [],
        [PublicAttr("value")],
        lambda sys: sys.send("this", "set-value", value=sys.send("args", "get-value")),
        {
            "add": PublicMethod(
                lambda sys: env.new_tmp_primitive(
                    sys.send("this", "get-value")
                    + sys.send(sys.send("args", "get-value"), "get-value"),
                )
            ),
            "sub": PublicMethod(
                lambda sys: env.new_tmp_primitive(
                    sys.send("this", "get-value")
                    - sys.send(sys.send("args", "get-value"), "get-value"),
                )
            ),
            "multiply": PublicMethod(
                lambda sys: env.new_tmp_primitive(
                    sys.send("this", "get-value")
                    * sys.send(sys.send("args", "get-value"), "get-value"),
                )
            ),
            "max": PublicMethod(
                lambda sys: env.new_tmp_primitive(
                    max(
                        sys.send("this", "get-value"),
                        sys.send(sys.send("args", "get-value"), "get-value"),
                    ),
                )
            ),
            "set-value": PublicMethod(
                lambda sys: sys.environment.get_instance("this").attributes.update(
                    value=sys.send(sys.send("args", "get-value"), "get-value")
                )
            ),
        },
    )
