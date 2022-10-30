from threading import Thread

from loguru import logger as LoguruLogger

from peekl.alertmanager import AlertManager
from peekl.database import RedisHandler
from peekl.helpers import load_config
from peekl.pollers import cert_validity_poller, status_poller


class Peekl:
    """Peekl class."""

    def __init__(self, config_path: str, logger: LoguruLogger) -> None:
        """Init of Peekl class.

        Args:
            config_path: str representation of a config file path
        """
        self._logger = logger
        self._logger.info("Starting Peekl worker...")
        self._config = load_config(config_path=config_path)
        self._logger.info(
            f"Successfully loaded configuration file : {config_path}"
        )
        self._redis_handler = RedisHandler(config=self._config.redis)
        self._alert_managers = AlertManager(
            config=self._config.alertmanagers,
            redis_handler=self._redis_handler,
        )

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
                    args=(website, self._redis_handler, self._alert_managers),
                    daemon=True,
                )
                t.start()
            self._redis_handler.create_timeseries(
                website.generate_timeseries_name()
            )
            self._logger.info(
                f"Starting HTTP monitoring daemon for {website.url} ..", end=""
            )
            t = Thread(
                target=status_poller,
                args=(website, self._redis_handler, self._alert_managers),
                daemon=True,
            )
            t.start()
        self._logger.info("Peekl worker successfully started.")
