from typing import Any, List

from app.helpers.environment import env

from .log import LogSettings


class AppSettings:
    app_name: str = env("APP_NAME", "spartan")
    environment: str = env("APP_ENVIRONMENT", "test")
    debug: bool = env("APP_DEBUG", False)
    allowed_origins: List[str] = [
        o.strip() for o in env("ALLOWED_ORIGINS", "*").split(",")
    ]

    log: LogSettings = LogSettings()

    def __call__(self, dotted_key: str, default: Any = None) -> Any:
        """
        Allow dynamic access via dot-notation:
        e.g. config("log.level") → "DEBUG"
        """
        keys = dotted_key.split(".")
        current = self
        for key in keys:
            if hasattr(current, key):
                current = getattr(current, key)
            else:
                return default
        return current


config = AppSettings()
