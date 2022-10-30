from datetime import datetime
from time import sleep

from requests import get

from peekl.alertmanager import AlertManager
from peekl.database import RedisHandler
from peekl.helpers import get_certificate
from peekl.models import Website


def status_poller(
    website: Website, redis_handler: RedisHandler, alert_manager: AlertManager
) -> None:
    """Get status from a website.

    Args:
        website: An instanciated Website object
        redis_handler: An instanciated RedisHandler used to push data
        alertmanagers: List of alertmanagers to send alert if needed
    """
    while True:
        headers = {"User-Agent": "peekl/http-monitoring"}
        req = get(website.url, headers=headers)
        if req.status_code in website.non_acceptable_status:
            alert_manager.send_alert_http(
                level="critical",
                status_code=req.status_code,
                website=website,
            )
        redis_handler.insert_timeseries_data(
            name=website.generate_timeseries_name(), value=req.status_code
        )
        sleep(website.interval)


def cert_validity_poller(
    website: Website, redis_handler: RedisHandler, alert_manager: AlertManager
) -> None:
    """Get validity from certificate and push it to Redis.

    Args:
        website: An instanciated Website object
        redis_handler: An instanciated RedisHandler used to push data
        alertmanagers: List of alertmanagers to send alert if needed
    """
    while True:
        certificate = get_certificate(website=website)
        certificate_date = datetime.strptime(
            certificate["notAfter"], "%b %d %H:%M:%S %Y %Z"
        )
        days_remaining = (certificate_date - datetime.now()).days
        match days_remaining:
            case _ if days_remaining < website.cert_critical:
                alert_manager.send_alert_cert(
                    level="critical",
                    remaining_days=days_remaining,
                    website=website,
                )
            case _ if days_remaining < website.cert_warning:
                alert_manager.send_alert_cert(
                    level="warning",
                    remaining_days=days_remaining,
                    website=website,
                )
        redis_handler.insert_timeseries_data(
            name=f"cert_{website.generate_timeseries_name()}",
            value=days_remaining,
        )
        sleep(website.certificate_monitoring_interval)
