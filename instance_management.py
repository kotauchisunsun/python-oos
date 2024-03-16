from class_definitions import Class
from typing import Dict, Any
from instance import Instance


class InstanceManagement:
    def __init__(self, instances: Dict[str, Instance] = {}) -> None:
        self.instances = instances

    def make_instance(
        self, _class: Class, instance_name: str, **argv: Dict[str, Any]
    ) -> Instance:
        instance = Instance(_class, instance_name, _class.get_default_attr())
        self.instances[instance_name] = instance
        return instance

    def get_instance(self, instance_name: str) -> Instance:
        return self.instances[instance_name]
