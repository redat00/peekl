from dataclasses import asdict
from threading import Thread

from loguru import logger as LoguruLogger

from peekl.alertmanager import generate_alert_manager
from peekl.database import RedisHandler
from peekl.helpers import cert_validity_poller, load_config, status_poller


class Peekl:
    """Peekl class."""

    def __init__(self, config_path: str, logger: LoguruLogger) -> None:
        """Init of Peekl class.

        Args:
            config_path: str representation of a config file path
        """
        self._logger = logger
        self._logger.info("Starting Peekl worker...")
        self._config = load_config(config_path)
        self._logger.info(f"Successfully loaded configuration file : {config_path}")
        self._alert_managers = [
            generate_alert_manager(manager_type, config)
            for manager_type, config in asdict(self._config.alertmanagers).items()
        ]
        self._redis_handler = RedisHandler(config=self._config.redis)

    def start(self) -> None:
        """Start threads to monitor website."""
        for website in self._config.websites:
            if website.certificate_monitoring:
                self._redis_handler.create_timeseries(
                    website.generate_timeseries_name()
                )
                self._logger.info(
                    f"Starting CERT monitoring daemon for {website.url} ..",
                )
                t = Thread(
                    target=cert_validity_poller,
                    args=(website, self._redis_handler),
                    daemon=True,
                )
                t.start()
            self._redis_handler.create_timeseries(website.generate_timeseries_name())
            self._logger.info(
                f"Starting HTTP monitoring daemon for {website.url} ..", end=""
            )
            t = Thread(
                target=status_poller,
                args=(website, self._redis_handler),
                daemon=True,
            )
            t.start()
        self._logger.info("Peekl worker successfully started.")
