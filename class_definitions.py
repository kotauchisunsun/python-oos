from dataclasses import dataclass
from method_accessor import PublicMethod,PrivateMethod
from attr_accessor import PublicAttr,PrivateAttr,ReadonlyAttr
from exceptions import MethodNotFound

@dataclass
class Class:
    name:str
    bases:tuple
    fields:tuple
    constructor:callable
    methods:dict

    @staticmethod
    def build(name,bases,fields,constructor,methods={}):
        _methods = dict(methods)

        #自動でsetter/getter
        for attr in fields:
            attr_name = attr.name
            def getter(sys,this,**args):
                return this.attributes[attr_name]
            def setter(sys,this,**args):
                this.attributes[attr_name] = args["value"]

            GetterMethodClass,SetterMethodClass = {
                PublicAttr: (PublicMethod,PublicMethod),
                PrivateAttr: (PrivateMethod,PrivateMethod),
                ReadonlyAttr: (PublicMethod,PrivateMethod)
            }[type(attr)]

            _methods[f"get-{attr_name}"] = GetterMethodClass(getter)
            _methods[f"set-{attr_name}"] = SetterMethodClass(setter)

        return Class(name,bases,fields,constructor,_methods)

    def get_method(self,name):
        if name not in self.methods:
            raise MethodNotFound(f"{method} not found")
        return self.methods[name]

class ClassDefinitions:
    def __init__(self):
        self.classes = {}

    def define(self,name,bases,fields,constructor,methods={}):
        self.classes[name] = Class.build(name,bases,fields,constructor,methods)

    def get_class(self,name):
        return self.classes[name]