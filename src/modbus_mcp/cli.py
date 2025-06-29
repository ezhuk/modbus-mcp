import asyncio
import typer

from modbus_mcp.server import ModbusMCP


app = typer.Typer(
    name="modbus-mcp",
    help="ModbusMCP CLI",
)


@app.command()
def run():
    server = ModbusMCP()
    asyncio.run(server.run_async(transport="http"))
