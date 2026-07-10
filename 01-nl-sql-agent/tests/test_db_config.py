"""Tests for db_config — stdlib only, no LangChain/MySQL needed."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db_config import build_mysql_uri, get_db_config, get_mysql_uri_from_env  # noqa: E402


class TestBuildMysqlUri:
    def test_standard_uri(self):
        uri = build_mysql_uri("root", "secret", "db.example.com", "3306", "Chinook")
        assert uri == "mysql+mysqlconnector://root:secret@db.example.com:3306/Chinook"

    def test_uses_mysqlconnector_driver(self):
        assert build_mysql_uri("u", "p", "h", "1", "d").startswith("mysql+mysqlconnector://")


class TestEnvConfig:
    def test_missing_password_raises(self, monkeypatch):
        monkeypatch.delenv("MYSQL_PASSWORD", raising=False)
        with pytest.raises(KeyError):
            get_db_config()

    def test_defaults_applied(self, monkeypatch):
        for var in ["MYSQL_USERNAME", "MYSQL_HOST", "MYSQL_PORT", "MYSQL_DATABASE"]:
            monkeypatch.delenv(var, raising=False)
        monkeypatch.setenv("MYSQL_PASSWORD", "pw")
        cfg = get_db_config()
        assert cfg == {"username": "root", "password": "pw", "host": "localhost",
                       "port": "3306", "database": "Chinook"}

    def test_env_to_uri_roundtrip(self, monkeypatch):
        monkeypatch.setenv("MYSQL_PASSWORD", "pw")
        monkeypatch.setenv("MYSQL_HOST", "10.0.0.5")
        uri = get_mysql_uri_from_env()
        assert "pw@10.0.0.5:3306/Chinook" in uri

    def test_no_hardcoded_credentials_in_source(self):
        # Guard: the lab's hardcoded password must never reappear
        src_dir = os.path.join(os.path.dirname(__file__), "..")
        for fname in ["sql_agent.py", "db_config.py"]:
            with open(os.path.join(src_dir, fname)) as f:
                content = f.read()
            assert "nVEOA1iQqBOz4cftLGdhXuTu" not in content
            assert "172.21.47.178" not in content


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
