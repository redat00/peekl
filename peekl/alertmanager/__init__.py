from typing import Any

from dacite import from_dict

from peekl.alertmanager.slack import Slack
from peekl.models import SlackConfig

alert_manager_mapper = {
    "slack": [Slack, SlackConfig],
}


def generate_alert_manager(manager_type: str, config: dict) -> Any:
    """Generate a fully configured alert manager based on a mapper.

    Args:
        manager_type: str representation of a manager type (eg. slack)
        config: A alert manager config
    """
    am = alert_manager_mapper[manager_type][0]
    return am(from_dict(data_class=alert_manager_mapper[manager_type][1], data=config))
