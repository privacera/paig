import os
import sys
import pandas as pd
import logging
from core.exceptions import UnauthorizedException
from werkzeug.security import check_password_hash
from core.config import load_config_file

logger = logging.getLogger(__name__)


class UserDataService:
    """User authentication service using an in-memory DataFrame."""
    _instance = None
    user_data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserDataService, cls).__new__(cls)
            cls._instance._load_user_data()
        return cls._instance

    def _load_user_data(self):
        """Loads the user authentication data from CSV."""
        logger = logging.getLogger(__name__)
        config = load_config_file()
        security_conf = config.get("security", {})
        basic_auth_config = security_conf.get("basic_auth", {})

        user_secrets_path = basic_auth_config.get("credentials_path")

        if not user_secrets_path:
            logger.warning("User secrets CSV file path not provided")
            sys.exit("User secrets CSV file path not provided")

        if not os.path.exists(user_secrets_path):
            logger.error(f"User secrets CSV file not found at {user_secrets_path}")
            sys.exit(f"User secrets CSV file not found at {user_secrets_path}")

        try:
            user_secrets_df = pd.read_csv(user_secrets_path)
            if user_secrets_df.empty:
                logger.error(f"User secrets CSV file is empty, File Path: {user_secrets_path}")
                sys.exit(f"User secrets CSV file is empty, File Path: {user_secrets_path}")

            required_columns = {"Username", "Secrets"}
            if not required_columns.issubset(user_secrets_df.columns):
                logger.error("User authentication data format error: Missing required columns")
                sys.exit("User authentication data format error: Missing required columns")

            self.user_data = user_secrets_df

        except Exception as e:
            logger.error(f"Error while reading user secrets CSV file, File Path: {user_secrets_path}, Error: {e}")
            sys.exit(f"Error while reading user secrets CSV file, File Path: {user_secrets_path}, Error: {e}")

    def verify_user_credentials(self, user_name: str, user_secret: str):
        """Validates the given user_name and password against the DataFrame."""
        if not user_secret:
            logger.warning(f"No password provided for user_name: {user_name}")
            raise UnauthorizedException("Invalid user_name or password")

        user_record = self.user_data[self.user_data["Username"] == user_name]

        if user_record.empty:
            raise UnauthorizedException("Invalid user_name or password")

        stored_hashed_password = user_record.iloc[0]["Secrets"]

        if not stored_hashed_password:
            logger.warning(f"No stored hashed password for user_name: {user_name}")
            raise UnauthorizedException("Invalid user_name or password")

        if not check_password_hash(stored_hashed_password, user_secret):
            raise UnauthorizedException("Invalid user_name or password")

        return {
            "user_name": user_name
        }
            

