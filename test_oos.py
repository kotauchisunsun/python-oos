from typing import Any
import pytest
from exceptions import MethodAccessDenied
from method_accessor import PrivateMethod, PublicMethod
from oos import ObjectOrientedSystem
from attr_accessor import PublicAttr, PrivateAttr, ReadonlyAttr


def test_attr() -> None:
    system = ObjectOrientedSystem()
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[PublicAttr("yen")],
        constructor=lambda sys: sys.send(
            "this", "set-yen", value=sys.send("args", "get-yen")
        ),
    )
    system.send("env", "new", cls="bank", name="my-account", yen=100)
    assert system.send("my-account", "get-yen") == 100


def test_default_attr_value() -> None:
    system = ObjectOrientedSystem()
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[PublicAttr("yen", 10)],
    )
    system.send("env", "new", cls="bank", name="my-account")
    assert system.send("my-account", "get-yen") == 10


def test_public_attr() -> None:
    system = ObjectOrientedSystem()
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[PublicAttr("dollars")],
        constructor=lambda sys: sys.send(
            "this", "set-dollars", value=sys.send("args", "get-dollars")
        ),
    )
    system.send("env", "new", cls="bank", name="my-account", dollars=100)
    assert system.send("my-account", "get-dollars") == 100
    system.send("my-account", "set-dollars", value=200)
    assert system.send("my-account", "get-dollars") == 200


def test_private_attr() -> None:
    system = ObjectOrientedSystem()
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[PrivateAttr("dollars")],
        constructor=lambda sys: sys.send(
            "this", "set-dollars", value=sys.send("args", "get-dollars")
        ),
    )
    system.send("env", "new", cls="bank", name="my-account", dollars=100)
    with pytest.raises(MethodAccessDenied):
        system.send("my-account", "get-dollars")
    with pytest.raises(MethodAccessDenied):
        system.send("my-account", "set-dollars")


def test_readonly_attr() -> None:
    system = ObjectOrientedSystem()
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[ReadonlyAttr("dollars")],
        constructor=lambda sys: sys.send(
            "this", "set-dollars", value=sys.send("args", "get-dollars")
        ),
    )
    system.send("env", "new", cls="bank", name="my-account", dollars=100)
    assert system.send("my-account", "get-dollars") == 100
    with pytest.raises(MethodAccessDenied):
        system.send("my-account", "set-dollars", value=200)


def test_bank() -> None:
    system = ObjectOrientedSystem()
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[PublicAttr("dollars")],
        constructor=lambda sys: sys.send(
            "this", "set-dollars", value=sys.send("args", "get-dollars")
        ),
        methods={
            "deposit": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars")
                    + sys.send("args", "get-value"),
                )
            ),
            "withdraw": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-dollars",
                    value=max(
                        0,
                        sys.send("this", "get-dollars") - sys.send("args", "get-value"),
                    ),
                )
            ),
        },
    )
    system.send("env", "new", cls="bank", name="my-account", dollars=100)
    system.send("my-account", "deposit", value=50)
    assert system.send("my-account", "get-dollars") == 150
    system.send("my-account", "withdraw", value=200)
    assert system.send("my-account", "get-dollars") == 0


def test_public_method() -> None:
    system = ObjectOrientedSystem()
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[PublicAttr("dollars")],
        constructor=lambda sys: sys.send(
            "this", "set-dollars", value=sys.send("args", "get-dollars")
        ),
        methods={
            "deposit": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars")
                    + sys.send("args", "get-value"),
                )
            ),
        },
    )
    system.send("env", "new", cls="bank", name="my-account", dollars=100)
    system.send("my-account", "deposit", value=50)


def test_private_method() -> None:
    system = ObjectOrientedSystem()
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[PublicAttr("dollars")],
        constructor=lambda sys: sys.send(
            "this", "set-dollars", value=sys.send("args", "get-dollars")
        ),
        methods={
            "deposit": PrivateMethod(
                lambda sys: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars")
                    + sys.send("args", "get-value"),
                )
            ),
        },
    )
    system.send("env", "new", cls="bank", name="my-account", dollars=100)
    with pytest.raises(MethodAccessDenied):
        system.send("my-account", "deposit", value=50)


# ポリモーフィズムのテスト
def test_polymorphism() -> None:
    system = ObjectOrientedSystem()
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[PublicAttr("dollars")],
        constructor=lambda sys: sys.send(
            "this", "set-dollars", value=sys.send("args", "get-dollars")
        ),
        methods={
            "deposit_by_dollar": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars")
                    + sys.send("args", "get-value"),
                )
            ),
            "withdraw": PrivateMethod(
                lambda sys: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars")
                    - sys.send("args", "get-value"),
                )
            ),
            "send": PublicMethod(
                lambda sys: (
                    sys.send(
                        sys.send("args", "get-to"),
                        "deposit_by_dollar",
                        value=sys.send("args", "get-amount"),
                    ),
                    sys.send("this", "withdraw", value=sys.send("args", "get-amount")),
                )
            ),
        },
    )
    system.send(
        "env",
        "define",
        name="japan_bank",
        attrs=[PublicAttr("yen")],
        constructor=lambda sys: sys.send(
            "this", "set-yen", value=sys.send("args", "get-yen")
        ),
        methods={
            "deposit_by_dollar": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-yen",
                    value=sys.send("this", "get-yen")
                    + sys.send("args", "get-value") * 150,
                )
            ),
        },
    )
    system.send("env", "new", cls="bank", name="source_bank", dollars=100)
    system.send("env", "new", cls="bank", name="target_dollar_bank", dollars=200)
    system.send("env", "new", cls="japan_bank", name="target_yen_bank", yen=500)

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
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[PublicAttr("dollars")],
        constructor=lambda sys: sys.send(
            "this", "set-dollars", value=sys.send("args", "get-dollars")
        ),
        methods={},
    )
    system.send(
        "env",
        "define",
        name="japan_bank",
        bases=["bank"],
        attrs=[PublicAttr("yen")],
        methods={},
    )
    system.send("env", "new", cls="japan_bank", name="my-account")
    system.send("my-account", "set-dollars", value=100)
    assert system.send("my-account", "get-dollars") == 100
    system.send("my-account", "set-yen", value=10)
    assert system.send("my-account", "get-yen") == 10


def test_inheritance_method() -> None:
    system = ObjectOrientedSystem()
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[PublicAttr("dollars")],
        constructor=lambda sys: sys.send(
            "this", "set-dollars", value=sys.send("args", "get-dollars")
        ),
        methods={
            "deposit_by_dollar": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars")
                    + sys.send("args", "get-value"),
                )
            ),
        },
    )
    system.send(
        "env",
        "define",
        name="japan_bank",
        bases=["bank"],
        attrs=[PublicAttr("yen")],
        methods={
            "deposit_by_yen": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-yen",
                    value=sys.send("this", "get-yen") + sys.send("args", "get-value"),
                )
            ),
        },
    )
    system.send("env", "new", cls="japan_bank", name="my-account")
    system.send("my-account", "set-dollars", value=100)
    system.send("my-account", "set-yen", value=10)
    system.send("my-account", "deposit_by_dollar", value=200)
    assert system.send("my-account", "get-dollars") == 300
    system.send("my-account", "deposit_by_yen", value=20)
    assert system.send("my-account", "get-yen") == 30


def test_inheritance_chain_method() -> None:
    system = ObjectOrientedSystem()
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[PublicAttr("dollars")],
        methods={
            "deposit_by_dollar": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars")
                    + sys.send("args", "get-value"),
                )
            ),
        },
    )
    system.send(
        "env",
        "define",
        name="japan_bank",
        bases=["bank"],
        attrs=[PublicAttr("yen")],
        methods={
            "deposit_by_yen": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-yen",
                    value=sys.send("this", "get-yen") + sys.send("args", "get-value"),
                )
            ),
        },
    )
    system.send(
        "env",
        "define",
        name="franc_bank",
        bases=["japan_bank"],
        attrs=[PublicAttr("franc")],
        methods={
            "deposit_by_franc": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-franc",
                    value=sys.send("this", "get-franc") + sys.send("args", "get-value"),
                )
            ),
        },
    )

    system.send("env", "new", cls="franc_bank", name="my-account")
    system.send("my-account", "set-dollars", value=100)
    assert system.send("my-account", "get-dollars") == 100
    system.send("my-account", "deposit_by_dollar", value=200)
    assert system.send("my-account", "get-dollars") == 300


def test_multiple_inheritance() -> None:
    system = ObjectOrientedSystem()
    system.send(
        "env",
        "define",
        name="bank",
        attrs=[PublicAttr("dollars")],
        methods={
            "deposit_by_dollar": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send("this", "get-dollars")
                    + sys.send("args", "get-value"),
                )
            ),
        },
    )
    system.send(
        "env",
        "define",
        name="japan_bank",
        attrs=[PublicAttr("yen")],
        methods={
            "deposit_by_yen": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-yen",
                    value=sys.send("this", "get-yen") + sys.send("args", "get-value"),
                )
            ),
        },
    )
    system.send(
        "env",
        "define",
        name="multi_bank",
        bases=["bank", "japan_bank"],
        methods={},
    )

    system.send("env", "new", cls="multi_bank", name="my-account")
    system.send("my-account", "set-dollars", value=100)
    assert system.send("my-account", "get-dollars") == 100
    system.send("my-account", "deposit_by_dollar", value=200)
    assert system.send("my-account", "get-dollars") == 300

    system.send("my-account", "set-yen", value=10)
    assert system.send("my-account", "get-yen") == 10
    system.send("my-account", "deposit_by_yen", value=20)
    assert system.send("my-account", "get-yen") == 30


def test_virtual_bank() -> None:
    def new_bank(dollars: int) -> dict[str, Any]:
        attrs: dict[str, Any] = {"dollars": dollars}

        def deposit(value: int) -> None:
            attrs["dollars"] += value

        def withdraw(value: int) -> None:
            attrs["dollars"] = max(0, attrs["dollars"] - value)

        attrs["deposit"] = deposit
        attrs["withdraw"] = withdraw
        return attrs

    my_account = new_bank(200)
    assert my_account["dollars"] == 200
    my_account["deposit"](50)
    assert my_account["dollars"] == 250
    my_account["withdraw"](100)
    assert my_account["dollars"] == 150
    my_account["withdraw"](200)
    assert my_account["dollars"] == 0
