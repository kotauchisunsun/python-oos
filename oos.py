import random
from attr_accessor import PublicAttr
from environment import Environment
from method_accessor import PublicMethod, PrivateMethod
from instance import Instance
from exceptions import MethodAccessDenied
from typing import Any
from class_definitions import MessageType


class ObjectOrientedSystem:
    def __init__(self) -> None:
        self.environment = Environment()

        def define(sys: ObjectOrientedSystem) -> None:
            self.environment.define(
                sys.send("args", "get-name"),
                sys.send("args", "get", attr="bases", fallback=[]),
                [
                    # intの時はintへ持ち替える
                    type(p)(p.name, self.convert_value(p.value))
                    for p in sys.send("args", "get", attr="attrs", fallback=[])
                ],
                sys.send("args", "get", attr="constructor", fallback=lambda sys: None),
                sys.send("args", "get", attr="methods", fallback={}),
            )

        def new(sys: ObjectOrientedSystem) -> Instance:
            cls = sys.send("args", "get-cls")
            name = sys.send("args", "get-name")

            if cls == "int":
                instance = self.environment.new_tmp_int(
                    sys.send(sys.send("args", "get-value"), "get-value")
                )
                self.environment.register_instance(name, instance)
                return instance

            instance = self.environment.new(cls, name)

            with self.environment:
                self.environment.register_instance("this", instance)
                instance.class_type.constructor(self)
                return instance

        self.environment.define(
            "environment",
            [],
            [],
            lambda sys: None,
            {"define": PublicMethod(define), "new": PublicMethod(new)},
        )

        env = self.environment.new("environment", "env")
        self.environment.register_instance("env", env)

    def send(
        self, instance_name: str | Instance, method: str, **argv: MessageType
    ) -> Any:
        if isinstance(instance_name, str):
            instance = self.environment.get_instance(instance_name)
        else:
            instance = instance_name

        if instance_name == "env":
            _argv = self.instantiate_argv(argv)
            self.environment.register_instance("args", _argv)
            return self.__call(instance, method)

        with self.environment:
            _argv = self.instantiate_argv(argv)
            self.environment.register_instance("args", _argv)
            self.environment.register_instance("this", instance)
            if instance_name == "this":
                return self.__call(instance, method)

            f = instance.get_method(method)
            if isinstance(f, PrivateMethod):
                raise MethodAccessDenied(f"{method} is PrivateMethod")
            elif isinstance(f, PublicMethod):
                return self.__call(instance, method)

    def convert_value(self, value: Any) -> Any:
        if isinstance(value, int):
            return self.environment.new_tmp_int(value)
        return value

    def instantiate_argv(self, argv: dict[str, MessageType]) -> Instance:
        _argv = {k: self.convert_value(v) for k, v in argv.items()}

        name = "args%f" % random.random()
        self.environment.define(
            name,
            [],
            [PublicAttr(k, v) for k, v in _argv.items()],
            lambda sys: None,
            {
                "get": PublicMethod(
                    lambda sys: sys.send("this", "get-" + sys.send("args", "get-attr"))
                    if sys.send("args", "get-attr") in argv
                    else sys.send("args", "get-fallback")
                ),
            },
        )
        return self.environment.new(name, "args")

    def __call(self, instance: Instance, method: str) -> Any:
        f = instance.get_method(method)
        return f.method(self)
