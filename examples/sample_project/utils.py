"""Utility functions and classes for the sample project."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any


class Logger:
    """Simple logging wrapper for the application."""

    def __init__(self, name: str, level: int = logging.INFO) -> None:
        """Initialize the logger.

        Args:
            name: Logger name (usually module name)
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create console handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(level)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message.

        Args:
            message: Message to log
            **kwargs: Additional context
        """
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message.

        Args:
            message: Message to log
            **kwargs: Additional context
        """
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message.

        Args:
            message: Message to log
            **kwargs: Additional context
        """
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message.

        Args:
            message: Message to log
            **kwargs: Additional context
        """
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message.

        Args:
            message: Message to log
            **kwargs: Additional context
        """
        self.logger.critical(message, extra=kwargs)


class ConfigManager:
    """Configuration manager for loading and managing app settings."""

    _instance = None
    _config: dict[str, Any] = {}

    def __new__(cls) -> "ConfigManager":
        """Implement singleton pattern.

        Returns:
            ConfigManager instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def load_config(cls, config_path: str | Path) -> "ConfigManager":
        """Load configuration from a file.

        Args:
            config_path: Path to configuration file (JSON or YAML)

        Returns:
            ConfigManager instance with loaded config

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        config_path = Path(config_path)

        if not config_path.exists():
            # Return default config if file doesn't exist
            cls._config = cls._get_default_config()
            return cls()

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                if config_path.suffix == ".json":
                    cls._config = json.load(f)
                elif config_path.suffix in [".yaml", ".yml"]:
                    # In real implementation, would use PyYAML
                    # For demo purposes, just use default config
                    cls._config = cls._get_default_config()
                else:
                    raise ValueError(f"Unsupported config format: {config_path.suffix}")
        except Exception as e:
            raise ValueError(f"Failed to load config: {e}") from e

        return cls()

    @staticmethod
    def _get_default_config() -> dict[str, Any]:
        """Get default configuration.

        Returns:
            Default configuration dictionary
        """
        return {
            "app_name": "Sample Project",
            "version": "1.0.0",
            "debug": False,
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "sampledb",
            },
            "payment_gateway": {
                "provider": "stripe",
                "api_key": "sk_test_example",
                "webhook_secret": "whsec_example",
            },
            "logging": {
                "level": "INFO",
                "format": "json",
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation, e.g., 'database.host')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def __getattr__(self, name: str) -> Any:
        """Allow attribute-style access to config values.

        Args:
            name: Configuration key

        Returns:
            Configuration value

        Raises:
            AttributeError: If key not found
        """
        if name.startswith("_"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        value = self._config.get(name)
        if value is None:
            raise AttributeError(f"Configuration key '{name}' not found")

        # Wrap dict values in ConfigManager for nested access
        if isinstance(value, dict):
            wrapper = ConfigManager()
            wrapper._config = value
            return wrapper

        return value


class DateTimeHelper:
    """Helper class for date and time operations."""

    @staticmethod
    def now() -> datetime:
        """Get current datetime.

        Returns:
            Current datetime
        """
        return datetime.now()

    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime as string.

        Args:
            dt: Datetime to format
            format_str: Format string

        Returns:
            Formatted datetime string
        """
        return dt.strftime(format_str)

    @staticmethod
    def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """Parse datetime from string.

        Args:
            dt_str: Datetime string
            format_str: Format string

        Returns:
            Parsed datetime

        Raises:
            ValueError: If string doesn't match format
        """
        return datetime.strptime(dt_str, format_str)

    @staticmethod
    def time_ago(dt: datetime) -> str:
        """Get human-readable time difference from now.

        Args:
            dt: Datetime to compare

        Returns:
            Human-readable time difference (e.g., "2 hours ago")
        """
        now = datetime.now()
        diff = now - dt

        seconds = diff.total_seconds()
        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"


class Validator:
    """Validation utilities for common data types."""

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format.

        Args:
            email: Email string to validate

        Returns:
            True if valid, False otherwise
        """
        if not email or "@" not in email:
            return False

        parts = email.split("@")
        if len(parts) != 2:
            return False

        local, domain = parts
        if not local or not domain:
            return False

        if "." not in domain:
            return False

        return True

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validate phone number format.

        Args:
            phone: Phone number string to validate

        Returns:
            True if valid, False otherwise
        """
        # Remove common formatting characters
        cleaned = (
            phone.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        )

        # Check if it contains only digits and optional + prefix
        if cleaned.startswith("+"):
            cleaned = cleaned[1:]

        return cleaned.isdigit() and len(cleaned) >= 10

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format.

        Args:
            url: URL string to validate

        Returns:
            True if valid, False otherwise
        """
        if not url:
            return False

        # Simple validation
        return url.startswith(("http://", "https://")) and "." in url


def sanitize_string(text: str, max_length: int | None = None) -> str:
    """Sanitize a string by removing dangerous characters.

    Args:
        text: String to sanitize
        max_length: Maximum length (truncate if longer)

    Returns:
        Sanitized string
    """
    # Remove any null bytes
    sanitized = text.replace("\x00", "")

    # Trim whitespace
    sanitized = sanitized.strip()

    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage.

    Args:
        part: Part value
        total: Total value

    Returns:
        Percentage (0-100)

    Raises:
        ValueError: If total is zero
    """
    if total == 0:
        raise ValueError("Total cannot be zero")

    return (part / total) * 100


def chunk_list(items: list[Any], chunk_size: int) -> list[list[Any]]:
    """Split a list into chunks of specified size.

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks

    Raises:
        ValueError: If chunk_size is less than 1
    """
    if chunk_size < 1:
        raise ValueError("Chunk size must be at least 1")

    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
