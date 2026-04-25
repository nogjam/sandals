class BindField:
    def __init__(self, name: str) -> None:
        self.name = name


class BindBaseMeta(type):
    def __init__(cls, name, bases, namespace, **kwds) -> None:
        try:
            annotations: dict[str, str] = namespace["__annotations__"]
        except KeyError:
            return
        cls._slots: list[str] = []
        for k in annotations.keys():
            setattr(cls, k, BindField(k))
            cls._slots.append(k)


class BindBase: ...
