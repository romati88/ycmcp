"""
Configuration constants and settings
"""

class Config:
    """Configuration constants for Yandex Cloud MCP Server"""
    
    # Environment variables
    TOKEN_ENV_VAR = "YC_TOKEN"
    FOLDER_ENV_VAR = "YC_FOLDER_ID"
    
    # Validation patterns
    TOKEN_PREFIX = "t1."
    FOLDER_ID_PATTERN = r'^[a-z0-9]{20}$'
    
    # Status messages
    CREDENTIALS_SUCCESS = "✅ Credentials configured successfully! You can now use list_vms and get_vm_config."
    CREDENTIALS_ERROR = "❌ Failed to configure credentials"
    TOKEN_NOT_CONFIGURED = "IAM token not configured. Please run setup_credentials first."
    FOLDER_NOT_CONFIGURED = "folder_id parameter is required. Please provide it or use setup_credentials to configure default folder_id."