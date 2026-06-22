import os
from dataclasses import dataclass


@dataclass
class Config:
    rapidapi_key: str = ""
    openai_api_key: str = ""
    debug: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            rapidapi_key=os.getenv("RAPIDAPI_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )
