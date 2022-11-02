from redis import Redis

from peekl.models import RedisConfig


class RedisHandler:
    """RedisHandler class."""

    def __init__(self, config: RedisConfig) -> None:
        """Init of RedisHandler class."""
        self._redis_client = Redis(
            host=config.host, port=config.port, db=config.db
        )

    def check_key_exists(self, name: str) -> bool:
        """Check wether a key exists inside of Redis or not.

        Args:
            name: str representation of the key name

        Returns:
            bool: True if key exists, else False
        """
        return bool(len(self._redis_client.keys(name)))

    def insert_data(self, name: str, data: str) -> None:
        """Insert data inside of redis.

        Args:
            name: Name of the key to be created
            data: data of the said key
        """
        self._redis_client.set(name=name, value=data)

    def delete_data(self, name: str) -> None:
        """Delete data from inside redis.

        Args:
            name: Name of data to be deleted
        """
        self._redis_client.delete(name)

    def create_timeseries(self, name: str) -> None:
        """Create of timeseries.

        Args:
            name: str representation of a timeseries name
        """
        if not self._redis_client.exists(name):
            self._redis_client.ts().create(key=name)

    def insert_timeseries_data(self, name: str, value: int) -> None:
        """Insert data inside of Redis database.

        Args:
            name: str representation of a timeseries name
            status: int representation of a http status
        """
        self._redis_client.ts().add(key=name, timestamp="*", value=value)
