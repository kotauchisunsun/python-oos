from dataclasses import dataclass

"""
- カプセル化
  - プライベート
  - パブリック
- 継承
- ポリモーフィズム
"""

@dataclass
class Instance:
    class_name: str
    name: str
    attributes: dict

@dataclass
class Class:
    name:str
    bases:tuple
    fields:tuple
    constructor:callable
    methods:dict

class ObjectOrientedSystem:
    def __init__(self):
        self.classes = {}
        self.instances = {}

    def def_class(self,name,bases,fields,constructor,methods={}):
        self.classes[name] = Class(name,bases,fields,constructor,methods)

    def get_instance(self,name):
        return self.instances[name]

    def make_instance(self,class_name,instance_name,**argv):
        _class = self.classes[class_name]
        instance = Instance(class_name,instance_name,dict())
        self.instances[instance_name] = instance
        _class.constructor(self,instance,**argv)
        return instance

    def call(self,obj,method,**argv):
        instance = self.instances[obj.name]
        methods = self.classes[instance.class_name].methods
        if method in methods:
            return methods[method](self,instance,**argv)
        else:
            prefix = "set-"
            if method.startswith(prefix):
                attr = method[len(prefix):]
                instance.attributes[attr] = argv["value"]
                return
            prefix = "get-"
            if method.startswith(prefix):
                attr = method[len(prefix):]
                return instance.attributes[attr]
            raise
