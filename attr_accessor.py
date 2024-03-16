from typing import Any, Union


class PublicAttr:
    def __init__(self, name: str, value: Any = None):
        self.name = name
        self.value = value


class PrivateAttr:
    def __init__(self, name: str, value: Any = None):
        self.name = name
        self.value = value


class ReadonlyAttr:
    def __init__(self, name: str, value: Any = None):
        self.name = name
        self.value = value


AttrType = Union[PublicAttr, PrivateAttr, ReadonlyAttr]
