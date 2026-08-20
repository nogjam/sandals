import typing as t


class BindAttr:
    def __init__[T: t.Any](self, type_: type[T], default_value: T) -> None:
        self.type = type_
        self.default_value = default_value


class BindBase: ...
