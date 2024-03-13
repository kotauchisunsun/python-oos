from dataclasses import dataclass
from method_accessor import PublicMethod,PrivateMethod
from attr_accessor import PublicAttr,PrivateAttr,ReadonlyAttr
from class_definitions import ClassDefinitions,Class
from instance import Instance,InstanceManagement
from exceptions import MethodAccessDenied

"""
- カプセル化
  - プライベート
  - パブリック
- 継承
- ポリモーフィズム
"""

"""
クラス未定義エラー
継承
"""

class InternalObjectOrientedSystem:
    def __init__(self):
        self.class_definitions = ClassDefinitions()
        self.instance_management = InstanceManagement()

    def def_class(self,name,bases,fields,constructor,methods={}):
        self.class_definitions.define(name,bases,fields,constructor,methods)

    def make_instance(self,class_name,instance_name,**argv):
        _class = self.class_definitions.get_class(class_name)
        return self.instance_management.make_instance(self,_class,instance_name,**argv)

    def send_to(self,instance_name,method,**argv):
        instance = self.instance_management.get_instance(instance_name)
        
        f = instance.class_type.get_method(method)
        if isinstance(f,PrivateMethod):
            raise MethodAccessDenied(f"{method} is PrivateMethod")
        elif isinstance(f,PublicMethod):
            return self.send(instance,method,**argv)
            
    def send(self,instance,method,**argv):
        f = instance.class_type.get_method(method)
        return f.method(self,instance,**argv)


class ObjectOrientedSystem:
    def __init__(self):
        self.sys = InternalObjectOrientedSystem()

    def def_class(self,name,bases,fields,constructor,methods={}):
        self.sys.def_class(name,bases,fields,constructor,methods)

    def make_instance(self,class_name,instance_name,**argv):
        return self.sys.make_instance(class_name,instance_name,**argv)

    def send_to(self,instance_name,method,**argv):
        return self.sys.send_to(instance_name,method,**argv)