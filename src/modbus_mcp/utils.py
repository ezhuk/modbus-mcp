from modbus_mcp.settings import Settings


def get_device(
    settings: Settings,
    name: str | None = None,
    host: str | None = None,
    port: int | None = None,
    unit: int | None = None,
) -> tuple[str, int, int]:
    """Find a device by name or return the default settings."""
    if name:
        for x in settings.devices:
            if x.name == name:
                return x.host, x.port, x.unit
        raise RuntimeError("Device not found")
    return (
        host if host is not None else settings.modbus.host,
        port if port is not None else settings.modbus.port,
        unit if unit is not None else settings.modbus.unit,
    )
