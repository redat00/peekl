from dataclasses import dataclass, field
from re import search
from typing import List, Optional


@dataclass
class AlertManagerConfigSkel:
    """Default model used for typing."""


@dataclass
class SlackConfig(AlertManagerConfigSkel):
    """SlackConfig models."""

    webhook: str
    manager_type: str = "slack"


@dataclass
class AlertManagers:
    """AlertManagers models."""

    slack: Optional[SlackConfig]


@dataclass
class RedisConfig:
    """RedisConfig models."""

    host: str
    port: int
    db: int


@dataclass
class Website:
    """Website models."""

    url: str
    port: int
    interval: int = 30
    certificate_monitoring: bool = False
    certificate_monitoring_interval: int = 30
    cert_warning: int = 30
    cert_critical: int = 5
    non_acceptable_status: List = field(
        default_factory=lambda: [
            400,
            401,
            402,
            403,
            404,
            405,
            406,
            407,
            408,
            410,
        ]
    )

    def generate_hostname(self) -> str:
        """Generate a hostname from url.

        This function will match the domain part of a URL and return it.

        Returns:
            str: The domain name of a URL
        """
        return search(
            r"(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/\n]+)",
            self.url,
        )[1]

    def generate_timeseries_name(self) -> str:
        """Generate a timeseries name from url.

        This function will replace all the "." and "://" by underscore in order
        to generate a more readable name for a timeseries.

        Returns:
            str: A timeseries name
        """
        return self.url.replace(".", "_").replace("://", "_")


@dataclass
class Config:
    """Config models."""

    redis: RedisConfig
    websites: List[Website]
    alertmanagers: Optional[AlertManagers]
