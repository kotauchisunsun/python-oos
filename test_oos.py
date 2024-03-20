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
    a = system.send("my-account", "get-yen")
    assert system.send(system.send("my-account", "get-yen"), "get-value") == 100
    b = system.send(system.send("my-account", "get-yen"), "add", value=100)
    assert system.send(b, "get-value") == 200


def test_int() -> None:
    system = ObjectOrientedSystem()
    system.send("env", "new", cls="int", name="x", value=10)
    assert system.send("x", "get-value") == 10


def test_int_add() -> None:
    system = ObjectOrientedSystem()
    system.send("env", "new", cls="int", name="x", value=10)
    assert system.send(system.send("x", "add", value=5), "get-value") == 15


def test_int_add_vars() -> None:
    system = ObjectOrientedSystem()
    system.send("env", "new", cls="int", name="x", value=10)
    system.send("env", "new", cls="int", name="y", value=5)
    assert system.send(system.send("x", "add", value="y"), "get-value") == 15


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
    assert system.send(system.send("my-account", "get-dollars"), "get-value") == 100
    system.send("my-account", "set-dollars", value=200)
    assert system.send(system.send("my-account", "get-dollars"), "get-value") == 200


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
    assert system.send(system.send("my-account", "get-dollars"), "get-value") == 100
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
                    value=sys.send(
                        sys.send("this", "get-dollars"),
                        "add",
                        value=sys.send("args", "get-value"),
                    ),
                )
            ),
            "withdraw": PublicMethod(
                lambda sys: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send(
                        sys.send(
                            sys.send("this", "get-dollars"),
                            "sub",
                            value=sys.send("args", "get-value"),
                        ),
                        "max",
                        value=0,
                    ),
                )
            ),
        },
    )
    system.send("env", "new", cls="bank", name="my-account", dollars=100)
    system.send("my-account", "deposit", value=50)
    assert system.send(system.send("my-account", "get-dollars"), "get-value") == 150
    system.send("my-account", "withdraw", value=200)
    assert system.send(system.send("my-account", "get-dollars"), "get-value") == 0


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
                    value=sys.send(
                        sys.send("this", "get-dollars"),
                        "add",
                        value=sys.send("args", "get-value"),
                    ),
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
                    value=sys.send(
                        sys.send("this", "get-dollars"),
                        "add",
                        value=sys.send("args", "get-value"),
                    ),
                )
            ),
            "withdraw": PrivateMethod(
                lambda sys: sys.send(
                    "this",
                    "set-dollars",
                    value=sys.send(
                        sys.send("this", "get-dollars"),
                        "sub",
                        value=sys.send("args", "get-value"),
                    ),
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
                    value=sys.send(
                        sys.send("this", "get-yen"),
                        "add",
                        value=sys.send(
                            sys.send("args", "get-value"), "multiply", value=150
                        ),
                    ),
                )
            ),
        },
    )
    system.send("env", "new", cls="bank", name="source_bank", dollars=100)
    system.send("env", "new", cls="bank", name="target_dollar_bank", dollars=200)
    system.send("env", "new", cls="japan_bank", name="target_yen_bank", yen=500)

    system.send("source_bank", "send", to="target_dollar_bank", amount=50)

    assert system.send(system.send("source_bank", "get-dollars"), "get-value") == 50
    assert (
        system.send(system.send("target_dollar_bank", "get-dollars"), "get-value")
        == 250
    )
    system.send("source_bank", "send", to="target_yen_bank", amount=50)
    assert system.send(system.send("source_bank", "get-dollars"), "get-value") == 0
    assert (
        system.send(system.send("target_yen_bank", "get-yen"), "get-value")
        == 500 + 50 * 150
    )


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
    assert system.send(system.send("my-account", "get-dollars"), "get-value") == 100
    system.send("my-account", "set-yen", value=10)
    assert system.send(system.send("my-account", "get-yen"), "get-value") == 10


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
                    value=sys.send(
                        sys.send("this", "get-dollars"),
                        "add",
                        value=sys.send("args", "get-value"),
                    ),
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
                    value=sys.send(
                        sys.send("this", "get-yen"),
                        "add",
                        value=sys.send("args", "get-value"),
                    ),
                )
            ),
        },
    )
    system.send("env", "new", cls="japan_bank", name="my-account")
    system.send("my-account", "set-dollars", value=100)
    system.send("my-account", "set-yen", value=10)
    system.send("my-account", "deposit_by_dollar", value=200)
    assert system.send(system.send("my-account", "get-dollars"), "get-value") == 300
    system.send("my-account", "deposit_by_yen", value=20)
    assert system.send(system.send("my-account", "get-yen"), "get-value") == 30


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
                    value=sys.send(
                        sys.send("this", "get-dollars"),
                        "add",
                        value=sys.send("args", "get-value"),
                    ),
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
                    value=sys.send(
                        sys.send("this", "get-yen"),
                        "add",
                        value=sys.send("args", "get-value"),
                    ),
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
                    value=sys.send(
                        sys.send("this", "get-franc"),
                        "add",
                        value=sys.send("args", "get-value"),
                    ),
                )
            ),
        },
    )

    system.send("env", "new", cls="franc_bank", name="my-account")
    system.send("my-account", "set-dollars", value=100)
    assert system.send(system.send("my-account", "get-dollars"), "get-value") == 100
    system.send("my-account", "deposit_by_dollar", value=200)
    assert system.send(system.send("my-account", "get-dollars"), "get-value") == 300


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
                    value=sys.send(
                        sys.send("this", "get-dollars"),
                        "add",
                        value=sys.send("args", "get-value"),
                    ),
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
                    value=sys.send(
                        sys.send("this", "get-yen"),
                        "add",
                        value=sys.send("args", "get-value"),
                    ),
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
    assert system.send(system.send("my-account", "get-dollars"), "get-value") == 100
    system.send("my-account", "deposit_by_dollar", value=200)
    assert system.send(system.send("my-account", "get-dollars"), "get-value") == 300

    system.send("my-account", "set-yen", value=10)
    assert system.send(system.send("my-account", "get-yen"), "get-value") == 10
    system.send("my-account", "deposit_by_yen", value=20)
    assert system.send(system.send("my-account", "get-yen"), "get-value") == 30


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
