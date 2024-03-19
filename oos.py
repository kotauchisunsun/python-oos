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

        def define(sys: ObjectOrientedSystem):
            self.environment.define(
                sys.send("args", "get-name"),
                sys.send("args", "get", attr="bases", fallback=[]),
                sys.send("args", "get", attr="attrs", fallback=[]),
                sys.send("args", "get", attr="constructor", fallback=lambda sys: None),
                sys.send("args", "get", attr="methods", fallback={}),
            )

        def new(sys: ObjectOrientedSystem):
            cls = sys.send("args", "get-cls")
            name = sys.send("args", "get-name")
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

    def send(self, instance_name: str, method: str, **argv: MessageType) -> Any:
        instance = self.environment.get_instance(instance_name)

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

    def instantiate_argv(self, argv):
        name = "args%f" % random.random()
        self.environment.define(
            name,
            [],
            [PublicAttr(k, v) for k, v in argv.items()],
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
