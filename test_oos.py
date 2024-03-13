from oos import *
import pytest

def test_attr():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (PublicAttr("yen"),), #属性
        lambda sys,this,**args:  sys.send(this,"set-yen",value=args["yen"]), #コンストラクタ
    )
    system.make_instance("bank","my-account",yen=100)
    assert system.send_to("my-account","get-yen") == 100 

def test_private_attr():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (PrivateAttr("dollars"),), #属性
        lambda sys,this,**args:  sys.send(this,"set-dollars",value=args["dollars"]), #コンストラクタ
    )
    system.make_instance("bank","my-account",dollars=100)
    with pytest.raises(MethodAccessDenied):
        system.send_to("my-account","get-dollars")
    with pytest.raises(MethodAccessDenied):
        system.send_to("my-account","set-dollars")

def test_readonly_attr():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (ReadonlyAttr("dollars"),), #属性
        lambda sys,this,**args:  sys.send(this,"set-dollars",value=args["dollars"]), #コンストラクタ
    )
    system.make_instance("bank","my-account",dollars=100)
    assert system.send_to("my-account","get-dollars") == 100 
    with pytest.raises(MethodAccessDenied):
        system.send_to("my-account","set-dollars",value=200)

def test_bank():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (PublicAttr("dollars"),), #属性
        lambda sys,this,**args:  sys.send(this,"set-dollars",value=args["dollars"]), #コンストラクタ
        methods = {
            "deposit": PublicMethod(lambda sys,this,**args: sys.send(this,"set-dollars",value=sys.send(this,"get-dollars")+args["value"])),
            "withdraw": PublicMethod(lambda sys,this,**args: sys.send(this,"set-dollars",value=max(0,sys.send(this,"get-dollars")-args["value"])))
        }
    )
    system.make_instance("bank","my-account",dollars=100)
    system.send_to("my-account","deposit",value=50)
    assert system.send_to("my-account","get-dollars") == 150 
    system.send_to("my-account","withdraw",value=200)
    assert system.send_to("my-account","get-dollars") == 0

def test_public_method():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (PublicAttr("dollars"),), #属性
        lambda sys,this,**args:  sys.send(this,"set-dollars",value=args["dollars"]), #コンストラクタ
        methods = {
            "deposit": PublicMethod(lambda sys,this,**args: sys.send(this,"set-dollars",value=sys.send(this,"get-dollars")+args["value"])),
        }
    )
    system.make_instance("bank","my-account",dollars=100)
    system.send_to("my-account","deposit",value=50)

def test_private_method():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (PublicAttr("dollars"),), #属性
        lambda sys,this,**args:  sys.send(this,"set-dollars",value=args["dollars"]), #コンストラクタ
        methods = {
            "deposit": PrivateMethod(lambda sys,this,**args: sys.send(this,"set-dollars",value=sys.send(this,"get-dollars")+args["value"])),
        }
    )
    system.make_instance("bank","my-account",dollars=100)
    with pytest.raises(MethodAccessDenied):
        system.send_to("my-account","deposit",value=50)

#ポリモーフィズムのテスト
def test_polymorphism():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        (PublicAttr("dollars"),), #属性
        lambda sys,this,**args:  sys.send(this,"set-dollars",value=args["dollars"]), #コンストラクタ
        methods = {
            "deposit_by_dollar": PublicMethod(lambda sys,this,**args: sys.send(this,"set-dollars",value=sys.send(this,"get-dollars")+args["value"])),
            "withdraw": PrivateMethod(lambda sys,this,**args: sys.send(this,"set-dollars",value=sys.send(this,"get-dollars")-args["value"])),
            "send": PublicMethod(
                lambda sys,this,**args: (sys.send_to(args["to"],"deposit_by_dollar",value=args["amount"]),sys.send(this,"withdraw",value=args["amount"]))
            ),
        }
    )
    system.def_class(
        "japan_bank", #クラス名
        tuple(), # 継承
        (PublicAttr("yen"),), #属性
        lambda sys,this,**args:  sys.send(this,"set-yen",value=args["yen"]), #コンストラクタ
        methods = {
            "deposit_by_dollar": PublicMethod(lambda sys,this,**args: sys.send(this,"set-yen",value=sys.send(this,"get-yen")+args["value"]*150)),
        }
    )
    system.make_instance("bank","source_bank",dollars=100)
    system.make_instance("bank","target_dollar_bank",dollars=200)
    system.make_instance("japan_bank","target_yen_bank",yen=500)

    system.send_to("source_bank","send",to="target_dollar_bank",amount=50)
    assert system.send_to("source_bank","get-dollars") == 50
    assert system.send_to("target_dollar_bank","get-dollars") == 250
    system.send_to("source_bank","send",to="target_yen_bank",amount=50)
    assert system.send_to("source_bank","get-dollars") == 0
    assert system.send_to("target_yen_bank","get-yen") == 500+50*150
