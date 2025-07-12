import pytest

from modbus_mcp.settings import Device, Settings
from modbus_mcp.utils import get_device


def test_get_device():
    settings = Settings()
    with pytest.raises(RuntimeError) as e:
        get_device(settings, "Foo")
    assert "not found" in str(e.value)
    assert get_device(settings) == ("127.0.0.1", 502, 1)
    assert get_device(settings, host="10.0.0.1", port=5020, unit=3) == (
        "10.0.0.1",
        5020,
        3,
    )
    settings.devices.append(Device(name="Foo", host="10.10.0.1", port=5020, unit=2))
    assert get_device(settings, name="Foo") == ("10.10.0.1", 5020, 2)
