from importlib.metadata import version

from modbus_mcp.server import ModbusMCP


__version__ = version("modbus-mcp")
__all__ = ["ModbusMCP"]
