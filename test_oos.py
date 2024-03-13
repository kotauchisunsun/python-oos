from oos import ObjectOrientedSystem

def test_attr():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        ("dollars",), #属性
        lambda sys,this,**args:  sys.call(this,"set-dollars",value=args["dollars"]), #コンストラクタ
    )
    instance = system.make_instance("bank","my-account",dollars=100)
    assert system.call(instance,"get-dollars") == 100 

def test_auto_attr():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        ("yen",), #属性
        lambda sys,this,**args:  sys.call(this,"set-yen",value=args["yen"]), #コンストラクタ
    )
    instance = system.make_instance("bank","my-account",yen=100)
    assert system.call(instance,"get-yen") == 100 

def test_method():
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        ("dollars",), #属性
        lambda sys,this,**args:  sys.call(this,"set-dollars",value=args["dollars"]), #コンストラクタ
        methods = {
            "deposit": lambda sys,this,**args: sys.call(this,"set-dollars",value=sys.call(this,"get-dollars")+args["value"]),
            "withdraw": lambda sys,this,**args: sys.call(this,"set-dollars",value=max(0,sys.call(this,"get-dollars")-args["value"]))
        }
    )
    instance = system.make_instance("bank","my-account",dollars=100)
    system.call(instance,"deposit",value=50)
    assert system.call(instance,"get-dollars") == 150 
    system.call(instance,"withdraw",value=200)
    assert system.call(instance,"get-dollars") == 0