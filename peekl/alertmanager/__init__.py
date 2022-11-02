from dataclasses import asdict
from datetime import datetime
from typing import Any

from dacite import from_dict

from peekl.alertmanager.slack import Slack
from peekl.database import RedisHandler
from peekl.models import AlertManagers, SlackConfig, Website

# alert_manager_mapper:
# Used to map a alert_manager type (an str) to it's corresponding class object
# as well as it's corresponding config models.
alert_manager_mapper = {
    "slack": [Slack, SlackConfig],
}


class AlertManager:
    """AlertManager config."""

    def __init__(
        self, config: AlertManagers, redis_handler: RedisHandler
    ) -> None:
        """AlertManager init.

        Args:
            config: AlertManagers instanciated object
            redis_handler: An instanciated RedisHandler object
        """
        self._ams = [
            self._generate_alert_manager(
                manager_type, asdict(config)[manager_type]
            )
            for manager_type in asdict(config)
        ]
        self._redis_handler = redis_handler

    def _generate_alert_manager(self, manager_type: str, config: dict) -> Any:
        """Generate a fully configured alert manager based on a mapper.

        Args:
            manager_type: str representation of a manager type (eg. slack)
            config: A alert manager config
        """
        am = alert_manager_mapper[manager_type][0]
        return am(
            from_dict(
                data_class=alert_manager_mapper[manager_type][1], data=config
            )
        )

    def send_alert_http(
        self, level: str, status_code: int, website: Website
    ) -> None:
        """Send HTTP alert to all AlertManagers.

        Args:
            level: level of alert, can be critical, warning or ok
            status_code: int representation of a HTTP status code
            website: An instanciated Website object
        """
        for am in self._ams:
            if not self._redis_handler.check_key_exists(
                f"http_{am.manager_type}_{website.generate_timeseries_name()}"
            ):
                am.send_alert_http(
                    level=level,
                    status_code=status_code,
                    website=website,
                )
                self._redis_handler.insert_data(
                    name=(
                        f"http_{am.manager_type}_"
                        f"{website.generate_timeseries_name()}"
                    ),
                    data=f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
                )

    def send_alert_cert(
        self, level: str, remaining_days: int, website: Website
    ) -> None:
        """Send CERT alert to slack.

        Args:
            message: Message that the alerts should contain
            level: str level of the alert (critical or warning)
        """
        for am in self._ams:
            if not self._redis_handler.check_key_exists(
                f"cert_{am.manager_type}_{website.generate_timeseries_name()}"
            ):
                am.send_alert_cert(
                    level=level,
                    remaining_days=remaining_days,
                    website=website,
                )
                self._redis_handler.insert_data(
                    name=(
                        f"cert_{am.manager_type}_"
                        f"{website.generate_timeseries_name()}"
                    ),
                    data=f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
                )

    def send_alert_ok(self, type: str, website: Website) -> None:
        """Send an OK alert and clear redis key.

        Args:
            type: can be either "cert" or "http"
        """
        for am in self._ams:
            am.send_alert_ok(type=type, website=website)
            self._redis_handler.delete_data(
                name=(
                    f"{type}_{am.manager_type}_"
                    f"{website.generate_timeseries_name()}"
                )
            )
