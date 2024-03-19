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

        def define(sys: ObjectOrientedSystem, **argv: Any):
            attr_or_fallback = (
                lambda name, default: sys.send("args", "get-%s" % name)
                if sys.send("args", "has", attr=name)
                else default
            )

            self.environment.define(
                sys.send("args", "get-name"),
                attr_or_fallback("bases", []),
                attr_or_fallback("attrs", []),
                attr_or_fallback("constructor", lambda sys: None),
                attr_or_fallback("methods", {}),
            )

        def new(sys: ObjectOrientedSystem, **argv: Any):
            cls = sys.send("args", "get-cls")
            name = sys.send("args", "get-name")
            instance = self.environment.new(cls, name, **argv)

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
            _argv = self.instantiate(argv)
            self.environment.register_instance("args", _argv)

            return self.__call(instance, method, **argv)

        with self.environment:
            _argv = self.instantiate(argv)
            self.environment.register_instance("args", _argv)

            self.environment.register_instance("this", instance)
            if instance_name == "this":
                return self.__call(instance, method, **argv)

            f = instance.get_method(method)
            if isinstance(f, PrivateMethod):
                raise MethodAccessDenied(f"{method} is PrivateMethod")
            elif isinstance(f, PublicMethod):
                return self.__call(instance, method, **argv)

    def instantiate(self, argv):
        name = "args%f" % random.random()
        self.environment.define(
            name,
            [],
            [PublicAttr(k, v) for k, v in argv.items()],
            lambda sys, **args: None,
            {"has": PublicMethod(lambda sys: sys.send("args", "get-attr") in argv)},
        )
        return self.environment.new(name, "args")

    def __call(self, instance: Instance, method: str, **argv: MessageType) -> Any:
        f = instance.get_method(method)
        return f.method(self)
