import os
from dataclasses import dataclass


@dataclass
class Config:
    rapidapi_key: str = ""
    anthropic_api_key: str = ""
    claude_model: str = "claude-haiku-4-5"
    debug: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            rapidapi_key=os.getenv("RAPIDAPI_KEY", ""),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            claude_model=os.getenv("CLAUDE_MODEL", "claude-haiku-4-5"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )
