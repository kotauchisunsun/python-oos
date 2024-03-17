from method_accessor import MethodType
from attr_accessor import AttrType
from exceptions import MethodNotFound
from typing import Iterable, Any, Callable, Protocol, Sequence

MessageType = Any
ClassConstructor = Callable[..., None]


class ClassInterface(Protocol):
    @property
    def attrs(self) -> list[AttrType]: ...

    @attrs.setter
    def attrs(self, attrs: list[AttrType]) -> None: ...

    @property
    def bases(self) -> Sequence["ClassInterface"]: ...

    @bases.setter
    def bases(self, bases: Sequence["ClassInterface"]) -> None: ...

    def get_default_attr(self) -> dict[str, AttrType]: ...
    def find_method(self, name: str) -> Iterable[MethodType]: ...
    def get_method(self, name: str) -> MethodType: ...


class Class(ClassInterface):
    def __init__(
        self,
        name: str,
        bases: Sequence[ClassInterface],
        attrs: list[AttrType],
        constructor: ClassConstructor,
        methods: dict[str, MethodType] = {},
    ) -> None:
        self.name = name
        self._bases = bases
        self._attrs = attrs
        self.constructor = constructor
        self.methods = methods

    @property
    def bases(self) -> Sequence[ClassInterface]:
        return self._bases

    @bases.setter
    def bases(self, bases: Sequence[ClassInterface]) -> None:
        self._bases = bases

    @property
    def attrs(self) -> list[AttrType]:
        return self._attrs

    @attrs.setter
    def attrs(self, attrs: list[AttrType]) -> None:
        self._attrs = attrs

    def get_default_attr(self) -> dict[str, AttrType]:
        attrs = {}
        for f in self.attrs:
            attrs[f.name] = f.value
        for base in self.bases:
            attrs.update(base.get_default_attr())
        return attrs

    def find_method(self, name: str) -> Iterable[MethodType]:
        if name in self.methods:
            yield self.methods[name]
            return
        for base in self.bases:
            for f in base.find_method(name):
                yield f
                return

    def get_method(self, name: str) -> MethodType:
        for f in self.find_method(name):
            return f
        raise MethodNotFound(f"{name} not found")
