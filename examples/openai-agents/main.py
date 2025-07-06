import asyncio

from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.model_settings import ModelSettings


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    for prompt in [
        "Read the content of 40010 on 127.0.0.1:502.",
        "Write [123, 45, 678] to registers starting at 40011.",
        "Read the value of 40012 holding register.",
    ]:
        print(f"Running: {prompt}")
        result = await Runner.run(starting_agent=agent, input=prompt)
        print(result.final_output)


async def main():
    async with MCPServerStreamableHttp(
        name="Streamable HTTP Server",
        params={
            "url": "http://localhost:8000/mcp/",
        },
    ) as server:
        await run(server)


if __name__ == "__main__":
    asyncio.run(main())
