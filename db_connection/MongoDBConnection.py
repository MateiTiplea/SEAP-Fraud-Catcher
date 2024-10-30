import json
import os
from typing import Optional
from urllib.parse import quote_plus

from dotenv import load_dotenv
from mongoengine import connect, disconnect


class MongoDBConnection:
    """
    Class to handle MongoDB connections using MongoEngine.
    Supports connection via direct parameters, a configuration file, or environment variables.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        authentication_database: Optional[str] = None,
        config_file: Optional[str] = None,
        env_file: Optional[str] = None,
    ):
        """
        Initialize the connection handler. Can use direct parameters, load from a config file, or from environment variables.

        Parameters:
        -----------
        host : str, optional
            The MongoDB host address.
        port : int, optional
            The MongoDB port.
        username : str, optional
            The MongoDB username.
        password : str, optional
            The MongoDB password.
        authentication_database : str, optional
            The authentication database to use.
        config_file : str, optional
            Path to a JSON config file containing the connection parameters.
        env_file : str, optional
            Path to an environment (.env) file containing the connection parameters.
        """
        # Load .env file if provided
        if env_file:
            load_dotenv(env_file)

        if config_file:
            self._load_from_config(config_file)
        else:
            # Use environment variables if available, or fallback to provided parameters
            self.host = host or os.getenv("MONGO_HOST")
            self.port = port or int(os.getenv("MONGO_PORT", 0))  # default 0 if not set
            self.username = username or os.getenv("MONGO_USERNAME")
            self.password = password or os.getenv("MONGO_PASSWORD")
            self.authentication_database = authentication_database or os.getenv(
                "MONGO_AUTH_DB"
            )

        self._is_connected = False
        self._validate_parameters()

    def _load_from_config(self, config_file: str):
        """Load connection settings from a JSON config file."""
        try:
            with open(config_file, "r") as file:
                config = json.load(file)

            self.host = config.get("host")
            self.port = config.get("port")
            self.username = config.get("username")
            self.password = config.get("password")
            self.authentication_database = config.get("authentication_database")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading configuration file: {e}")

    def _validate_parameters(self):
        """Validate essential connection parameters."""
        if not self.host:
            raise ValueError("MongoDB host must be specified.")
        if not isinstance(self.port, int) or self.port <= 0:
            raise ValueError("MongoDB port must be a positive integer.")
        if self.username is None or self.password is None:
            raise ValueError("MongoDB username and password must be specified.")

    def connect(self):
        """Establish a connection to MongoDB using MongoEngine."""
        if self._is_connected:
            raise ConnectionError("Already connected to MongoDB.")

        try:
            # Build the connection URI
            connection_uri = f"mongodb://{quote_plus(self.username)}:{quote_plus(self.password)}@{self.host}:{self.port}/?authSource={self.authentication_database}"
            print(f"Connecting to MongoDB at {connection_uri}...")

            # Connect to MongoDB using MongoEngine
            connect(
                db=self.authentication_database or "admin",
                host=connection_uri,
            )
            self._is_connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    def disconnect(self):
        """Disconnect from MongoDB."""
        if not self._is_connected:
            raise ConnectionError("Not connected to MongoDB.")
        disconnect(alias="default")
        self._is_connected = False

    def is_connected(self) -> bool:
        """Check if the connection is currently active."""
        return self._is_connected
