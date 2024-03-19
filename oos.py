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
            self.environment.define(
                argv["name"],
                argv.get("bases", []),
                argv.get("attrs", []),
                argv.get("constructor", lambda sys, **args: None),
                argv.get("methods", []),
            )

        def new(sys: ObjectOrientedSystem, **argv: Any):
            cls = argv["cls"]
            name = argv["name"]
            del argv["cls"]
            del argv["name"]
            instance = self.environment.new(cls, name, **argv)

            with self.environment:
                self.environment.register_instance("this", instance)
                instance.class_type.constructor(self, **argv)
                return instance

        self.environment.define(
            "environment",
            [],
            [],
            lambda sys, **args: None,
            {"define": PublicMethod(define), "new": PublicMethod(new)},
        )

        env = self.environment.new("environment", "env")
        self.environment.register_instance("env", env)

    def send(self, instance_name: str, method: str, **argv: MessageType) -> Any:
        instance = self.environment.get_instance(instance_name)

        if instance_name == "env":
            name = "args%f" % random.random()
            self.environment.define(
                name,
                [],
                [PublicAttr(k, v) for k, v in argv.items()],
                lambda sys, **args: None,
                {},
            )
            _argv = self.environment.new(name, "args")
            self.environment.register_instance("args", _argv)

            return self.__call(instance, method, **argv)

        with self.environment:
            name = "args%f" % random.random()
            self.environment.define(
                name,
                [],
                [PublicAttr(k, v) for k, v in argv.items()],
                lambda sys, **args: None,
                {},
            )
            _argv = self.environment.new(name, "args")
            self.environment.register_instance("args", _argv)

            self.environment.register_instance("this", instance)
            if instance_name == "this":
                return self.__call(instance, method, **argv)

            f = instance.get_method(method)
            if isinstance(f, PrivateMethod):
                raise MethodAccessDenied(f"{method} is PrivateMethod")
            elif isinstance(f, PublicMethod):
                return self.__call(instance, method, **argv)

    def __call(self, instance: Instance, method: str, **argv: MessageType) -> Any:
        f = instance.get_method(method)
        return f.method(self, **argv)
