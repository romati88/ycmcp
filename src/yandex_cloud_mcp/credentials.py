"""
Credential management functionality
"""

import os
import re
import logging
from typing import Optional
import yandexcloud
from .config import Config

logger = logging.getLogger(__name__)


class CredentialManager:
    """Manages Yandex Cloud credentials for the session"""
    
    def __init__(self):
        self._iam_token: Optional[str] = None
        self._folder_id: Optional[str] = None
    
    def set_credentials(self, iam_token: str, folder_id: str) -> None:
        """Set credentials for the session"""
        self._iam_token = iam_token if self._validate_token(iam_token) else None
        self._folder_id = folder_id if self._validate_folder_id(folder_id) else None
    
    def get_token(self) -> Optional[str]:
        """Get IAM token from session or environment"""
        return self._iam_token or os.getenv(Config.TOKEN_ENV_VAR)
    
    def get_folder_id(self) -> Optional[str]:
        """Get folder ID from session or environment"""
        return self._folder_id or os.getenv(Config.FOLDER_ENV_VAR)
    
    def clear(self) -> None:
        """Clear stored credentials"""
        self._iam_token = None
        self._folder_id = None
    
    @staticmethod
    def _validate_token(token: str) -> bool:
        """Validate IAM token format"""
        return token.startswith(Config.TOKEN_PREFIX) and len(token) > 50
    
    @staticmethod
    def _validate_folder_id(folder_id: str) -> bool:
        """Validate folder ID format"""
        return re.match(Config.FOLDER_ID_PATTERN, folder_id) is not None


def get_yc_sdk(credentials: CredentialManager) -> yandexcloud.SDK:
    """Initialize Yandex Cloud SDK with IAM token"""
    iam_token = credentials.get_token()
    if not iam_token:
        raise ValueError(Config.TOKEN_NOT_CONFIGURED)
    
    try:
        sdk = yandexcloud.SDK(iam_token=iam_token)
        logger.info("Successfully initialized Yandex Cloud SDK")
        return sdk
    except Exception as e:
        logger.error(f"Failed to initialize SDK: {str(e)}")
        raise ValueError(f"Failed to initialize Yandex Cloud SDK: {str(e)}")