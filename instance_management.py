from class_definitions import Class
from typing import Any
from instance import Instance


class InstanceManagement:
    def __init__(
        self,
    ) -> None:
        self.instances: list[dict[str, Instance]] = [{}]

    def make_instance(self, _class: Class, instance_name: str) -> Instance:
        instance = Instance.new_from_class(_class)
        self.instances[-1][instance_name] = instance
        return instance

    def register_instance(self, name: str, instance: Instance) -> None:
        self.instances[-1][name] = instance

    def get_instance(self, instance_name: str) -> Instance:
        for instances in reversed(self.instances):
            if instance_name in instances:
                return instances[instance_name]
        raise Exception(f"{instance_name} is not defined")

    def push(self) -> None:
        self.instances.append({})

    def pop(self) -> None:
        self.instances.pop()
