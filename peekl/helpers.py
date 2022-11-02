from os import path
from urllib.request import socket, ssl

from dacite import from_dict
from yaml import safe_load

from peekl.models import Config, Website


def load_config(config_path: str) -> Config:
    """Load configuration from file.

    Args:
        config_path: str path of a file

    Returns:
        Config: loaded from config file Config object
    """
    with open(config_path) as f:
        data = safe_load(f)
    return from_dict(data_class=Config, data=data)


def get_certificate(website: Website) -> dict:
    """Get certificate for a given website.

    Args:
        website: An instanciated Website object

    Returns:
        dict: certificate as dict
    """
    context = ssl.create_default_context()
    with socket.create_connection(
        (website.generate_hostname(), website.port)
    ) as sock:
        with context.wrap_socket(
            sock, server_hostname=website.generate_hostname()
        ) as ssock:
            return ssock.getpeercert()


def get_templates_dir() -> str:
    """Used to get alert managers templates directory path.

    Returns:
        str: Path to the templates directory
    """
    root_dir = path.dirname(path.abspath(__file__))
    return path.join(root_dir, "alertmanager/templates/")
