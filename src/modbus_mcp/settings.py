from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Auth(BaseModel):
    key: str | None = None


class Modbus(BaseModel):
    host: str = "127.0.0.1"
    port: int = 502
    unit: int = 1


class Settings(BaseSettings):
    auth: Auth = Auth()
    modbus: Modbus = Modbus()
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="MODBUS_MCP_",
    )
