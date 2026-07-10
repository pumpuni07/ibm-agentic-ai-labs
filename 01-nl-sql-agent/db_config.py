"""Database and credential configuration for the NL SQL Agent.

Standard-library-only helpers, unit-testable without LangChain or MySQL.

SECURITY NOTE: The original IBM lab hardcoded the MySQL password and host
of its temporary lab database directly in the script. This module replaces
that with environment variables so no credentials ever enter version
control.
"""

import os


def build_mysql_uri(username: str, password: str, host: str,
                    port: str, database: str) -> str:
    """Construct a SQLAlchemy MySQL connection URI (mysqlconnector driver)."""
    return (
        f"mysql+mysqlconnector://{username}:{password}"
        f"@{host}:{port}/{database}"
    )


def get_db_config() -> dict:
    """Read MySQL connection settings from environment variables.

    Required: MYSQL_PASSWORD
    Optional (with defaults): MYSQL_USERNAME=root, MYSQL_HOST=localhost,
    MYSQL_PORT=3306, MYSQL_DATABASE=Chinook

    Raises:
        KeyError: If MYSQL_PASSWORD is not set.
    """
    return {
        "username": os.environ.get("MYSQL_USERNAME", "root"),
        "password": os.environ["MYSQL_PASSWORD"],
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": os.environ.get("MYSQL_PORT", "3306"),
        "database": os.environ.get("MYSQL_DATABASE", "Chinook"),
    }


def get_mysql_uri_from_env() -> str:
    """Convenience: environment → ready-to-use connection URI."""
    return build_mysql_uri(**get_db_config())
