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
        initial_request = get(website.url, headers=headers)
        status_code = initial_request.status_code
        if status_code in website.non_acceptable_status:
            # For every entry inside of the website.retry attributes, will
            # fetch the website and set the status_code variable to his newly
            # obtain status_code
            for _ in range(website.retry):
                req = get(website.url, headers=headers)
                status_code = req.status_code
            # If status_code that has now the value of the last retry is still
            # in the non_acceptable_status, then now we will send an alert
            if status_code in website.non_acceptable_status:
                alert_manager.send_alert_http(
                    level="critical",
                    status_code=initial_request.status_code,
                    website=website,
                )
        elif (
            status_code not in website.non_acceptable_status
            and redis_handler.check_key_exists(
                f"http_*_{website.generate_timeseries_name()}"
            )
        ):
            alert_manager.send_alert_ok(
                type="http",
                website=website,
            )
        redis_handler.insert_timeseries_data(
            name=website.generate_timeseries_name(),
            value=status_code,
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
            case _ if redis_handler.check_key_exists(
                f"cert_*_{website.generate_timeseries_name()}"
            ):
                alert_manager.send_alert_ok(
                    type="cert",
                    website=website,
                )
        redis_handler.insert_timeseries_data(
            name=f"cert_{website.generate_timeseries_name()}",
            value=days_remaining,
        )
        sleep(website.certificate_monitoring_interval)
