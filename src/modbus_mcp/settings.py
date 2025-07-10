from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class Auth(BaseModel):
    key: str | None = None


class Modbus(BaseModel):
    host: str = "127.0.0.1"
    port: int = 502
    unit: int = 1


class Device(BaseModel):
    name: str
    host: str
    port: int
    unit: int


class Settings(BaseSettings):
    auth: Auth = Auth()
    modbus: Modbus = Modbus()
    devices: list[Device] = []
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="MODBUS_MCP_",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            JsonConfigSettingsSource(settings_cls, json_file="devices.json"),
        )
