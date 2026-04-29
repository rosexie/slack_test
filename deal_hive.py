import random
from typing import Any

from pyhive.hive import connect

try:
    from utils.logger import logger
except Exception:  # pragma: no cover - fallback logger for standalone usage
    import logging

    logger = logging.getLogger(__name__)


class DealHive:
    """Hive client wrapper with host failover and automatic reconnect."""

    def __init__(self, hosts: list[str] | None = None, port: int = 10000) -> None:
        self.hosts = hosts or ["persp-45", "persp-63"]
        self.port = port
        self.conn = None
        self.get_conn()

    def _open_conn(self, host: str):
        return connect(
            host=host,
            port=self.port,
            auth="KERBEROS",
            kerberos_service_name="hive",
        )

    def get_conn(self) -> None:
        hosts = self.hosts[:]
        random.shuffle(hosts)

        errors: list[str] = []
        self.conn = None
        for host in hosts:
            try:
                self.conn = self._open_conn(host)
                logger.info("Hive connected to %s", host)
                return
            except Exception as exc:
                errors.append(f"{host}: {exc}")
                logger.warning("Hive connection failed on %s: %s", host, exc)

        raise ConnectionError("Failed to connect to Hive. " + " | ".join(errors))

    def get_info(self, str_sql: str) -> list[tuple[Any, ...]]:
        try:
            return self.get_info_by_sql(str_sql)
        except Exception as exc:
            logger.error("DealHive get_info error: %s. Reconnecting and retrying once.", exc)
            self.get_conn()
            return self.get_info_by_sql(str_sql)

    def get_info_by_sql(self, str_sql: str) -> list[tuple[Any, ...]]:
        if self.conn is None:
            self.get_conn()

        with self.conn.cursor() as cursor:
            cursor.execute(str_sql)
            return cursor.fetchall()

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None
