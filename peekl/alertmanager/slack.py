from jinja2 import Template
from requests import put

from peekl.helpers import get_templates_dir
from peekl.models import SlackConfig, Website


class Slack:
    """Slack class for sending alerts."""

    def __init__(self, config: SlackConfig) -> None:
        """Init of class Slack.

        Args:
            config: An instanciated SlackConfig object.
        """
        self._config = config
        with open(f"{get_templates_dir()}slack/slack_http.j2") as f:
            self._http_template = Template(f.read())
        with open(f"{get_templates_dir()}slack/slack_cert.j2") as f:
            self._cert_template = Template(f.read())
        with open(f"{get_templates_dir()}slack/slack_ok.j2") as f:
            self._ok_template = Template(f.read())
        self.manager_type = config.manager_type

    def _generate_message(self):
        pass

    def _send_alert(self, message: str) -> None:
        """Send alert to slack."""
        headers = {"Content-Type": "application/json"}
        put(self._config.webhook, data=message, headers=headers)

    def send_alert_http(
        self, level: str, status_code: int, website: Website
    ) -> None:
        """Send HTTP alert to slack.

        Args:
            level: str level of the alert (critical or warning)
            status_code: status code of the error
            website: Website instanciated object
        """
        message = self._http_template.render(
            level=level,
            status_code=status_code,
            website=website.url,
        )
        self._send_alert(message)

    def send_alert_cert(
        self, level: str, remaining_days: int, website: Website
    ) -> None:
        """Send CERT alert to slack.

        Args:
            level: str level of the alert (critical or warning)
            remaining_days: number of days before certificates expire
            website: Website instanciated object
        """
        message = self._cert_template.render(
            level=level,
            remaining_days=remaining_days,
            website=website.url,
        )
        self._send_alert(message)

    def send_alert_ok(self, type: str, website: Website) -> None:
        """Send OK alert to slack.

        Args:
            type: type of alert that is now OK (can be "cert" or "http")
            website: Website instanciated object
        """
        message = self._ok_template.render(type=type, website=website.url)
        self._send_alert(message)
