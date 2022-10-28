from sys import stderr
from time import sleep

from click import Path, command, option
from loguru import logger as LoguruLogger

from peekl.worker import Peekl


@command
@option(
    "-c",
    "--config-file",
    help="path of the configuration file of the application",
    required=True,
    type=Path(exists=True),
)
def main(config_file: str) -> None:
    """Main command entrypoint for Peekl.

    Args:
        config_file: str representation of a file path
    """
    logger = LoguruLogger
    logger.remove()
    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
        "| <level>{level: <8}</level> | {message}"
    )
    logger.add(stderr, format=fmt)
    peekl = Peekl(config_path=config_file, logger=logger)
    peekl.start()
    while True:
        sleep(200)
