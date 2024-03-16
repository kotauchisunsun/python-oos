from typing import Union, Callable, Any


class PublicMethod:
    def __init__(self, method: Callable[..., Any]) -> None:
        self.method = method


class PrivateMethod:
    def __init__(self, method: Callable[..., Any]) -> None:
        self.method = method


MethodType = Union[PublicMethod, PrivateMethod]
