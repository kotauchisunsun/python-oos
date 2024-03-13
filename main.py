from oos import ObjectOrientedSystem

if __name__=="__main__":
    system = ObjectOrientedSystem()
    system.def_class(
        "bank", #クラス名
        tuple(), # 継承
        ("dollars",), #属性
        lambda sys,this,**args:  sys.call(this,"set-dollars",value=args["dollars"]), #コンストラクタ
        methods = {
            "deposit": lambda sys,this,**args: sys.call(this,"set-dollars",value=sys.call(this,"get-dollars")+args["value"]),
        }
    )
    system.make_instance("bank","my-account",dollars=100)
    instance = system.get_instance("my-account")
    print(system.call(instance,"get-dollars"))
    system.call(instance,"deposit",value=50)
    print(system.call(instance,"get-dollars"))
    