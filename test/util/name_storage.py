"""Utilities for storing names."""

import typing as t


class NameJacket:
    def __init__(self) -> None:
        # Start with an insignificant value.
        self._value: t.Any = None
        self._has_value: bool = False

    @property
    def value(self) -> t.Any:
        return self._value

    @value.setter
    def value(self, value: t.Any) -> None:
        self._value = value
        self._has_value = True

    @value.deleter
    def value(self) -> None:
        self._has_value = False

    @property
    def has_value(self) -> bool:
        return self._has_value

    @has_value.setter
    def has_value(self, value: bool) -> None:
        raise AttributeError("Cannot set has_value property")


class NameStorageMeta(type):
    """Implements type-annotation-based member variable declaration for
    NameStorage.
    """

    def __init__(cls, name, bases, namespace, **kwds) -> None:
        try:
            annotations: dict[str, str] = namespace["__annotations__"]
        except KeyError:
            return
        cls._slots: list[str] = []
        for k in annotations.keys():
            setattr(cls, k, NameJacket())
            cls._slots.append(k)


class NameStorage(metaclass=NameStorageMeta):
    """Parent class for namespaces with explicitly-defined, typed
    attributes."""

    def __setattr__(self, name: str, value: t.Any) -> None:
        """Sets the named attribute so that it now holds a value. The name must
        be one of the pre-defined slots.
        """
        cls: type = type(self)
        if hasattr(cls, name) and isinstance(jacket := getattr(cls, name), NameJacket):
            jacket.value = value
        else:
            raise AttributeError(f"Cannot set nonexistent attribute {name!r}")

    def __getattribute__(self, name: str) -> t.Any:
        """Returns the named attribute."""
        jacket: NameJacket = super().__getattribute__(name)
        if not isinstance(jacket, NameJacket):
            return jacket
        if not jacket.has_value:
            raise ValueError(f"Attribute {name!r} has not been set")
        return jacket.value

    def __delattr__(self, name: str) -> None:
        """Deletes the named attribute so that it no longer holds a value. The
        slot can be reassigned a value in the future.
        """
        cls: type = type(self)
        if isinstance(jacket := getattr(cls, name), NameJacket):
            del jacket.value
        else:
            raise AttributeError(f"Cannot delete nonexistent attribute {name!r}")
