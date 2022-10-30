from redis import Redis

from peekl.models import RedisConfig


class RedisHandler:
    """RedisHandler class."""

    def __init__(self, config: RedisConfig) -> None:
        """Init of RedisHandler class."""
        self.redis_client = Redis(
            host=config.host, port=config.port, db=config.db
        )

    def create_timeseries(self, name: str) -> None:
        """Create of timeseries.

        Args:
            name: str representation of a timeseries name
        """
        if not self.redis_client.exists(name):
            self.redis_client.ts().create(key=name)

    def insert_timeseries_data(self, name: str, value: int) -> None:
        """Insert data inside of Redis database.

        Args:
            name: str representation of a timeseries name
            status: int representation of a http status
        """
        self.redis_client.ts().add(key=name, timestamp="*", value=value)
