from datetime import datetime
from time import sleep
from urllib.request import socket, ssl

from dacite import from_dict
from requests import get
from yaml import safe_load

from peekl.database import RedisHandler
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
    with socket.create_connection((website.generate_hostname(), website.port)) as sock:
        with context.wrap_socket(
            sock, server_hostname=website.generate_hostname()
        ) as ssock:
            return ssock.getpeercert()


def status_poller(website: Website, redis_handler: RedisHandler) -> None:
    """Get status from a website.

    Args:
        website: An instanciated Website object
        redis_handler: An instanciated RedisHandler used to push data
    """
    while True:
        headers = {"User-Agent": "peekl/http-monitoring"}
        req = get(website.url, headers=headers)
        redis_handler.insert_data(
            name=website.generate_timeseries_name(), value=req.status_code
        )
        sleep(website.interval)


def cert_validity_poller(website: Website, redis_handler: RedisHandler) -> None:
    """Get validity from certificate and push it to Redis.

    Args:
        website: An instanciated Website object
        redis_handler: An instanciated RedisHandler used to push data
    """
    while True:
        certificate = get_certificate(website=website)
        certificate_date = datetime.strptime(
            certificate["notAfter"], "%b %d %H:%M:%S %Y %Z"
        )
        redis_handler.insert_data(
            name=f"cert_{website.generate_timeseries_name()}",
            value=(certificate_date - datetime.now()).days,
        )
        sleep(website.certificate_monitoring_interval)
