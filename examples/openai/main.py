import asyncio
import os

from openai import AsyncOpenAI


SERVER_NAME = "modbus-mcp"
SERVER_URL = "http://127.0.0.1:8000/mcp"


client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


async def create_response(msg):
    print(f"Running: {msg}")
    return await client.responses.create(
        model="gpt-4.1",
        tools=[
            {
                "type": "mcp",
                "server_label": SERVER_NAME,
                "server_url": SERVER_URL,
                "allowed_tools": ["read_registers", "write_registers"],
                "require_approval": "never",
            }
        ],
        input=msg,
    )


async def main():
    resp = await create_response("Read the content of 40010 on 127.0.0.1:502.")
    print(resp.output_text)

    resp = await create_response("Write [123, 45, 678] to registers starting at 40011.")
    print(resp.output_text)

    resp = await create_response("Read the value of 40012 holding register.")
    print(resp.output_text)


if __name__ == "__main__":
    asyncio.run(main())
