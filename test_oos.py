from oos import ObjectOrientedSystem
import pytest
from attr_accessor import PublicAttr, PrivateAttr, ReadonlyAttr
from method_accessor import PublicMethod, PrivateMethod
from exceptions import MethodAccessDenied
from typing import Dict, Any


def test_attr() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [PublicAttr("yen")],
        lambda sys, **args: sys.send("this", "set-yen", value=args["yen"]),
    )
    system.make_instance("bank", "my-account", yen=100)
    assert system.send("my-account", "get-yen") == 100


def test_default_attr_value() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [
            PublicAttr("yen", 10),
        ],
    )
    system.make_instance("bank", "my-account")
    assert system.send("my-account", "get-yen") == 10


def test_public_attr() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [
            PublicAttr("dollars"),
        ],
        lambda sys, **args: sys.send("this", "set-dollars", value=args["dollars"]),
    )
    system.make_instance("bank", "my-account", dollars=100)
    assert system.send("my-account", "get-dollars") == 100
    system.send("my-account", "set-dollars", value=200)
    assert system.send("my-account", "get-dollars") == 200


def test_private_attr() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [
            PrivateAttr("dollars"),
        ],
        lambda sys, **args: sys.send("this", "set-dollars", value=args["dollars"]),
    )
    system.make_instance("bank", "my-account", dollars=100)
    with pytest.raises(MethodAccessDenied):
        system.send("my-account", "get-dollars")
    with pytest.raises(MethodAccessDenied):
        system.send("my-account", "set-dollars")


def test_readonly_attr() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [ReadonlyAttr("dollars")],
        lambda sys, **args: sys.send("this", "set-dollars", value=args["dollars"]),
    )
    system.make_instance("bank", "my-account", dollars=100)
    assert system.send("my-account", "get-dollars") == 100
    with pytest.raises(MethodAccessDenied):
        system.send("my-account", "set-dollars", value=200)


def test_bank() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [PublicAttr("dollars")],
        lambda sys, **args: sys.send("this", "set-dollars", value=args["dollars"]),
        methods={
            "deposit": PublicMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars") + args["value"],
                )
            ),
            "withdraw": PublicMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-dollars",
                    value=max(0, sys.send("this", "get-dollars") - args["value"]),
                )
            ),
        },
    )
    system.make_instance("bank", "my-account", dollars=100)
    system.send("my-account", "deposit", value=50)
    assert system.send("my-account", "get-dollars") == 150
    system.send("my-account", "withdraw", value=200)
    assert system.send("my-account", "get-dollars") == 0


def test_public_method() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [PublicAttr("dollars")],
        lambda sys, **args: sys.send("this", "set-dollars", value=args["dollars"]),
        methods={
            "deposit": PublicMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars") + args["value"],
                )
            ),
        },
    )
    system.make_instance("bank", "my-account", dollars=100)
    system.send("my-account", "deposit", value=50)


def test_private_method() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [PublicAttr("dollars")],
        lambda sys, **args: sys.send("this", "set-dollars", value=args["dollars"]),
        methods={
            "deposit": PrivateMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars") + args["value"],
                )
            ),
        },
    )
    system.make_instance("bank", "my-account", dollars=100)
    with pytest.raises(MethodAccessDenied):
        system.send("my-account", "deposit", value=50)


# ポリモーフィズムのテスト
def test_polymorphism() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [PublicAttr("dollars")],
        lambda sys, **args: sys.send("this", "set-dollars", value=args["dollars"]),
        methods={
            "deposit_by_dollar": PublicMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars") + args["value"],
                )
            ),
            "withdraw": PrivateMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars") - args["value"],
                )
            ),
            "send": PublicMethod(
                lambda sys, **args: (
                    sys.send(args["to"], "deposit_by_dollar", value=args["amount"]),
                    sys.send("this", "withdraw", value=args["amount"]),
                )
            ),
        },
    )
    system.def_class(
        "japan_bank",
        [],
        [PublicAttr("yen")],
        lambda sys, **args: sys.send("this", "set-yen", value=args["yen"]),
        methods={
            "deposit_by_dollar": PublicMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-yen",
                    value=sys.send("this", "get-yen") + args["value"] * 150,
                )
            ),
        },
    )
    system.make_instance("bank", "source_bank", dollars=100)
    system.make_instance("bank", "target_dollar_bank", dollars=200)
    system.make_instance("japan_bank", "target_yen_bank", yen=500)

    system.send("source_bank", "send", to="target_dollar_bank", amount=50)

    print(system.send("source_bank", "get-dollars"))
    print(system.send("target_dollar_bank", "get-dollars"))
    print(system.send("target_yen_bank", "get-yen"))

    assert system.send("source_bank", "get-dollars") == 50
    assert system.send("target_dollar_bank", "get-dollars") == 250
    system.send("source_bank", "send", to="target_yen_bank", amount=50)
    assert system.send("source_bank", "get-dollars") == 0
    assert system.send("target_yen_bank", "get-yen") == 500 + 50 * 150


def test_inheritance_getter_setter() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [PublicAttr("dollars")],
        lambda sys, **args: sys.send("this", "set-dollars", value=args["dollars"]),
        methods={},
    )
    system.def_class(
        "japan_bank",
        ["bank"],
        [PublicAttr("yen")],
        methods={},
    )
    system.make_instance("japan_bank", "my-account")
    system.send("my-account", "set-dollars", value=100)
    assert system.send("my-account", "get-dollars") == 100
    system.send("my-account", "set-yen", value=10)
    assert system.send("my-account", "get-yen") == 10


def test_inheritance_method() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [PublicAttr("dollars")],
        lambda sys, **args: sys.send("this", "set-dollars", value=args["dollars"]),
        methods={
            "deposit_by_dollar": PublicMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars") + args["value"],
                )
            ),
        },
    )
    system.def_class(
        "japan_bank",
        ["bank"],
        [PublicAttr("yen")],
        methods={
            "deposit_by_yen": PublicMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-yen",
                    value=sys.send("this", "get-yen") + args["value"],
                )
            ),
        },
    )
    system.make_instance("japan_bank", "my-account")
    system.send("my-account", "set-dollars", value=100)
    system.send("my-account", "set-yen", value=10)
    system.send("my-account", "deposit_by_dollar", value=200)
    assert system.send("my-account", "get-dollars") == 300
    system.send("my-account", "deposit_by_yen", value=20)
    assert system.send("my-account", "get-yen") == 30


def test_inheritance_chain_method() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [PublicAttr("dollars")],
        methods={
            "deposit_by_dollar": PublicMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars") + args["value"],
                )
            ),
        },
    )
    system.def_class(
        "japan_bank",
        ["bank"],
        [PublicAttr("yen")],
        methods={
            "deposit_by_yen": PublicMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-yen",
                    value=sys.send("this", "get-yen") + args["value"],
                )
            ),
        },
    )
    system.def_class(
        "franc_bank",
        ["japan_bank"],
        [PublicAttr("franc")],
        methods={
            "deposit_by_franc": PublicMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-franc",
                    value=sys.send("this", "get-franc") + args["value"],
                )
            ),
        },
    )

    system.make_instance("franc_bank", "my-account")
    system.send("my-account", "set-dollars", value=100)
    assert system.send("my-account", "get-dollars") == 100
    system.send("my-account", "deposit_by_dollar", value=200)
    assert system.send("my-account", "get-dollars") == 300


def test_multiple_inheritance() -> None:
    system = ObjectOrientedSystem()
    system.def_class(
        "bank",
        [],
        [PublicAttr("dollars")],
        methods={
            "deposit_by_dollar": PublicMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars") + args["value"],
                )
            ),
        },
    )
    system.def_class(
        "japan_bank",
        [],
        [PublicAttr("yen")],
        methods={
            "deposit_by_yen": PublicMethod(
                lambda sys, **args: sys.send(
                    "this",
                    "set-yen",
                    value=sys.send("this", "get-yen") + args["value"],
                )
            ),
        },
    )
    system.def_class(
        "multi_bank",
        ["bank", "japan_bank"],
        [],
        methods={},
    )

    system.make_instance("multi_bank", "my-account")
    system.send("my-account", "set-dollars", value=100)
    assert system.send("my-account", "get-dollars") == 100
    system.send("my-account", "deposit_by_dollar", value=200)
    assert system.send("my-account", "get-dollars") == 300

    system.send("my-account", "set-yen", value=10)
    assert system.send("my-account", "get-yen") == 10
    system.send("my-account", "deposit_by_yen", value=20)
    assert system.send("my-account", "get-yen") == 30


def test_virtual_bank() -> None:
    def new_bank(dollars: int) -> Dict[str, Any]:
        return {"dollars": dollars}

    def deposit(bank: Dict[str, Any], value: int) -> None:
        bank["dollars"] += value

    def withdraw(bank: Dict[str, Any], value: int) -> None:
        bank["dollars"] = max(0, bank["dollars"] - value)

    my_account = new_bank(200)
    assert my_account["dollars"] == 200
    deposit(my_account, 50)
    assert my_account["dollars"] == 250
    withdraw(my_account, 100)
    assert my_account["dollars"] == 150
    withdraw(my_account, 200)
    assert my_account["dollars"] == 0
