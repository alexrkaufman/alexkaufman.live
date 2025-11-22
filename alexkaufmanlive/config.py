"""Application configuration with dev and prod environments."""

import asyncio
import logging
import os

from onepassword.client import Client


class BaseConfig:
    """Base configuration shared by all environments."""

    # Database
    DATABASE: str = "alexkaufmanlive.sqlite"

    # Logging
    LOG_LEVEL: int = logging.INFO


class DevConfig(BaseConfig):
    """Development configuration."""

    # Security
    SECRET_KEY: str = "dev-secret-key-not-for-production"

    # External services (disabled in dev)
    GITHUB_WEBHOOK_SECRET: str | None = None
    BUTTONDOWN_API_TOKEN: str | None = None

    # Logging
    LOG_LEVEL: int = logging.DEBUG


class ProdConfig(BaseConfig):
    """Production configuration loaded from 1Password."""

    # Default values (used if 1Password is not available)
    SECRET_KEY: str = "dev"
    GITHUB_WEBHOOK_SECRET: str | None = None
    BUTTONDOWN_API_TOKEN: str | None = None

    # Logging
    LOG_LEVEL: int = logging.WARNING

    # 1Password secret references
    # Format: op://vault/item/field
    _SECRET_REFS = {
        "SECRET_KEY": "op://alexkaufman.live/prod_site/secret_key",
        "DATABASE": "op://alexkaufman.live/prod_site/database",
        "GITHUB_WEBHOOK_SECRET": "op://alexkaufman.live/github-webhook/secret",
        "BUTTONDOWN_API_TOKEN": "op://alexkaufman.live/buttondown/api-token",
    }

    @classmethod
    async def _load_secrets_async(cls) -> dict:
        """Load secrets from 1Password asynchronously."""
        token = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
        if not token:
            print("Warning: OP_SERVICE_ACCOUNT_TOKEN not set, using default values")
            return {}

        try:
            client = await Client.authenticate(
                auth=token,
                integration_name="alexkaufman.live",
                integration_version="v1.0.0",
            )

            secrets = {}
            for key, ref in cls._SECRET_REFS.items():
                try:
                    value = await client.secrets.resolve(ref)
                    secrets[key] = value
                except Exception as e:
                    print(f"Warning: Could not load {key} from 1Password: {e}")

            return secrets

        except Exception as e:
            print(f"Error authenticating with 1Password: {e}")
            return {}

    @classmethod
    def load_secrets(cls) -> None:
        """Load secrets from 1Password synchronously."""
        try:
            secrets = asyncio.run(cls._load_secrets_async())

            # Update class attributes with loaded secrets
            for key, value in secrets.items():
                setattr(cls, key, value)

            print(f"Loaded {len(secrets)} secrets from 1Password")

        except Exception as e:
            print(f"Error loading secrets: {e}")
            print("Using default configuration values")


# Determine which config to use based on environment variable
# Default to dev for safety
environment = os.getenv("FLASK_ENV", "development")

if environment == "production":
    Config = ProdConfig
    Config.load_secrets()
else:
    Config = DevConfig
