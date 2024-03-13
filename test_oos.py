from oos import *
import pytest

def test_attr():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (PublicAttr("yen"),), #属性
        lambda sys,this,**args:  sys.call(this,"set-yen",value=args["yen"]), #コンストラクタ
    )
    system.make_instance("bank","my-account",yen=100)
    assert system.call("my-account","get-yen") == 100 

def test_private_attr():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (PrivateAttr("dollars"),), #属性
        lambda sys,this,**args:  sys.call(this,"set-dollars",value=args["dollars"]), #コンストラクタ
    )
    system.make_instance("bank","my-account",dollars=100)
    with pytest.raises(MethodAccessDenied):
        system.call("my-account","get-dollars")
    with pytest.raises(MethodAccessDenied):
        system.call("my-account","set-dollars")

def test_readonly_attr():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (ReadonlyAttr("dollars"),), #属性
        lambda sys,this,**args:  sys.call(this,"set-dollars",value=args["dollars"]), #コンストラクタ
    )
    system.make_instance("bank","my-account",dollars=100)
    assert system.call("my-account","get-dollars") == 100 
    with pytest.raises(MethodAccessDenied):
        system.call("my-account","set-dollars",value=200)

def test_bank():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (PublicAttr("dollars"),), #属性
        lambda sys,this,**args:  sys.call(this,"set-dollars",value=args["dollars"]), #コンストラクタ
        methods = {
            "deposit": PublicMethod(lambda sys,this,**args: sys.call(this,"set-dollars",value=sys.call(this,"get-dollars")+args["value"])),
            "withdraw": PublicMethod(lambda sys,this,**args: sys.call(this,"set-dollars",value=max(0,sys.call(this,"get-dollars")-args["value"])))
        }
    )
    system.make_instance("bank","my-account",dollars=100)
    system.call("my-account","deposit",value=50)
    assert system.call("my-account","get-dollars") == 150 
    system.call("my-account","withdraw",value=200)
    assert system.call("my-account","get-dollars") == 0

def test_public_method():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (PublicAttr("dollars"),), #属性
        lambda sys,this,**args:  sys.call(this,"set-dollars",value=args["dollars"]), #コンストラクタ
        methods = {
            "deposit": PublicMethod(lambda sys,this,**args: sys.call(this,"set-dollars",value=sys.call(this,"get-dollars")+args["value"])),
        }
    )
    system.make_instance("bank","my-account",dollars=100)
    system.call("my-account","deposit",value=50)

def test_private_method():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (PublicAttr("dollars"),), #属性
        lambda sys,this,**args:  sys.call(this,"set-dollars",value=args["dollars"]), #コンストラクタ
        methods = {
            "deposit": PrivateMethod(lambda sys,this,**args: sys.call(this,"set-dollars",value=sys.call(this,"get-dollars")+args["value"])),
        }
    )
    system.make_instance("bank","my-account",dollars=100)
    with pytest.raises(MethodAccessDenied):
        system.call("my-account","deposit",value=50)
