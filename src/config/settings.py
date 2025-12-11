# src/config/settings.py
from pydantic import BaseModel
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    oracle_user: str
    oracle_password: str
    oracle_dsn: str  # del estilo "localhost:1521/XEPDB1"

    @property
    def oracle_sqlalchemy_url(self) -> str:
        # Formato para Oracle + oracledb con service_name
        # oracle+oracledb://user:pass@host:port/?service_name=XEPDB1
        # Partimos el DSN "host:port/XEPDB1"
        host_port, service_name = self.oracle_dsn.split("/")
        host, port = host_port.split(":")
        return (
            f"oracle+oracledb://{self.oracle_user}:{self.oracle_password}"
            f"@{host}:{port}/?service_name={service_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings(
        oracle_user=os.getenv("ORACLE_USER", "retail"),
        oracle_password=os.getenv("ORACLE_PASSWORD", "retail"),
        oracle_dsn=os.getenv("ORACLE_DSN", "localhost:1521/XEPDB1"),
    )
