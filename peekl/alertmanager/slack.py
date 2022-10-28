from json import dumps

from requests import put

from peekl.models import SlackConfig


class Slack:
    """Slack class for sending alerts."""

    def __init__(self, config: SlackConfig) -> None:
        """Init of class Slack.

        Args:
            config: An instanciated SlackConfig object.
        """
        self._config = config

    def send_alert(self, message: str) -> None:
        """Send alert to slack.

        Args:
            message: Message that the alerts should contain
        """
        headers = {"Content-Type": "application/json"}
        data = {"text": message}
        put(self._config.webhook, data=dumps(data), headers=headers)
