from dataclasses import dataclass
from class_definitions import Class

@dataclass
class Instance:
    class_type: Class
    name: str
    attributes: dict

class InstanceManagement:
    def __init__(self):
        self.instances = {}

    def make_instance(self,sys,_class,instance_name,**argv):
        instance = Instance(_class,instance_name,dict())
        self.instances[instance_name] = instance
        _class.constructor(sys,instance,**argv)
        return instance

    def get_instance(self,instance_name):
        return self.instances[instance_name]
