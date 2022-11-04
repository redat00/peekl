from jinja2 import Template
from requests import post

from peekl.helpers import get_templates_dir
from peekl.models import DiscordConfig, Website


class Discord:
    """Discord alertmanager integration."""

    def __init__(self, config: DiscordConfig) -> None:
        """Init of Discord integration class.

        Args:
            config: Instanciated loaded from config file DiscordConfig object
        """
        self._config = config
        with open(f"{get_templates_dir()}discord/discord_http.j2") as f:
            self._http_template = Template(f.read())
        with open(f"{get_templates_dir()}discord/discord_cert.j2") as f:
            self._cert_template = Template(f.read())
        with open(f"{get_templates_dir()}discord/discord_ok.j2") as f:
            self._ok_template = Template(f.read())
        self.manager_type = config.manager_type

    def _send_alert(self, message: str) -> None:
        """Send alert to Discord.

        Args:
            message: str rendered message
        """
        headers = {"Content-Type": "application/json"}
        req = post(url=self._config.webhook, data=message, headers=headers)
        req.raise_for_status()

    def send_alert_http(
        self, level: str, status_code: int, website: Website
    ) -> None:
        """Send HTTP alert to Discord.

        Args:
            level: str level of the alert (critical or warning)
            status_code: status code of the error
            website: Website instanciated object
        """
        message = self._http_template.render(
            level=level,
            status_code=status_code,
            website=website.url,
            username=self._config.username,
        )
        self._send_alert(message)

    def send_alert_cert(
        self, level: str, remaining_days: int, website: Website
    ) -> None:
        """Send CERT alert to Discord

        Args:
            level: str level of the alert (critical or warning)
            remaining_days: number of days before certificates expire
            website: Website instanciated object
        """
        message = self._cert_template.render(
            level=level,
            remaining_days=remaining_days,
            website=website.url,
            username=self._config.username,
        )
        self._send_alert(message)

    def send_alert_ok(self, type: str, website: Website) -> None:
        """Send OK alert to Discord.

        Args:
            type: str representation of alert OK type (cert or http)
            website: Website instanciated object
        """
        message = self._ok_template.render(
            type=type,
            website=website.url,
            username=self._config.username,
        )
        self._send_alert(message)
