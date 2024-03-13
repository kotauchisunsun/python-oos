from dataclasses import dataclass

"""
- カプセル化
  - プライベート
  - パブリック
- 継承
- ポリモーフィズム
"""

class MethodAccessDenied(Exception):
    pass

class MethodNotFound(Exception):
    pass

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

class PublicMethod:
    def __init__(self,method):
        self.method = method

class PrivateMethod:
    def __init__(self,method):
        self.method = method

class PublicAttr:
    def __init__(self,name):
        self.name = name

class PrivateAttr:
    def __init__(self,name):
        self.name = name

class ReadonlyAttr:
    def __init__(self,name):
        self.name = name

class InternalObjectOrientedSystem:
    def __init__(self):
        self.classes = {}
        self.instances = {}

    def def_class(self,name,bases,fields,constructor,methods={}):
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

        self.classes[name] = Class(name,bases,fields,constructor,_methods)

    def make_instance(self,class_name,instance_name,**argv):
        _class = self.classes[class_name]
        instance = Instance(class_name,instance_name,dict())
        self.instances[instance_name] = instance
        _class.constructor(self,instance,**argv)
        return instance

    def call_by_name(self,instance_name,method,**argv):
        instance = self.instances[instance_name]
        methods = self.classes[instance.class_name].methods

        for name,f in methods.items():
            if name == method:
                if isinstance(f,PrivateMethod):
                    raise MethodAccessDenied(f"{method} is PrivateMethod")
                elif isinstance(f,PublicMethod):
                    return self.call(instance,method,**argv)

        raise MethodNotFound(f"{method} not found")

    def call(self,instance,method,**argv):
        methods = self.classes[instance.class_name].methods
        if method in methods:
            return methods[method].method(self,instance,**argv)
        else:
            raise MethodNotFound(f"{method} not found")

class ObjectOrientedSystem:
    def __init__(self):
        self.sys = InternalObjectOrientedSystem()

    def def_class(self,name,bases,fields,constructor,methods={}):
        self.sys.def_class(name,bases,fields,constructor,methods)

    def make_instance(self,class_name,instance_name,**argv):
        return self.sys.make_instance(class_name,instance_name,**argv)

    def call(self,instance_name,method,**argv):
        return self.sys.call_by_name(instance_name,method,**argv)