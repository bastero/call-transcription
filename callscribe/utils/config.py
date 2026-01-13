"""Configuration management."""

import os
from pathlib import Path
from dotenv import dotenv_values
from typing import Optional


class Config:
    """Application configuration."""

    def __init__(self):
        """Load configuration from environment variables."""
        # Find .env file in project root (parent of callscribe directory)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        env_path = project_root / '.env'

        # Load values from .env file
        env_values = dotenv_values(env_path) if env_path.exists() else {}

        # API Keys - try .env file first, then environment
        self.anthropic_api_key = env_values.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

        # Whisper Settings
        self.whisper_model = env_values.get("WHISPER_MODEL", os.getenv("WHISPER_MODEL", "base"))

        # Audio Settings
        self.sample_rate = int(env_values.get("SAMPLE_RATE", os.getenv("SAMPLE_RATE", "16000")))
        self.channels = int(env_values.get("CHANNELS", os.getenv("CHANNELS", "1")))

        # Claude Settings
        self.claude_model = env_values.get("CLAUDE_MODEL", os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307"))

    def validate(self) -> bool:
        """
        Validate that required configuration is present.

        Returns:
            True if valid, False otherwise
        """
        if not self.anthropic_api_key:
            print("❌ ANTHROPIC_API_KEY not found in .env file")
            return False

        print("✓ Configuration validated")
        return True

    def display(self):
        """Display current configuration (without sensitive data)."""
        print("\n=== Current Configuration ===")
        print(f"Whisper Model: {self.whisper_model}")
        print(f"Claude Model: {self.claude_model}")
        print(f"Sample Rate: {self.sample_rate} Hz")
        print(f"Channels: {self.channels}")
        print(f"API Key: {'Set' if self.anthropic_api_key else 'Not Set'}")
        print("=" * 30 + "\n")


def get_config() -> Config:
    """Get application configuration."""
    return Config()
