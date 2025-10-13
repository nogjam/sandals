import pytest

from test.util.name_storage import NameStorage


def test_name_storage() -> None:
    # With no annotations defined, the subclass is pretty useless.
    class NameStorageUseless(NameStorage):
        pass

    nc_useless: NameStorageUseless = NameStorageUseless()
    with pytest.raises(AttributeError):
        nc_useless.yo = 1
    with pytest.raises(AttributeError):
        nc_useless.yo

    class NameCapsuleTest(NameStorage):
        count: int
        mapping: dict[str, str]

    nc_test: NameCapsuleTest = NameCapsuleTest()

    # You cannot access an attribute that doesn't exist.
    with pytest.raises(AttributeError):
        nc_test.nonexistent

    # You cannot access an attribute that hasn't been set.
    with pytest.raises(ValueError):
        nc_test.count

    # You can set an attribute.
    nc_test.count = 1

    # Then you can get that attribute.
    assert hasattr(nc_test, "count")
    assert nc_test.count == 1

    # You can delete an attribute.
    del nc_test.count
    with pytest.raises(ValueError):
        nc_test.count
