#!/usr/bin/env python3
"""
Main MCP server implementation
"""

import logging
from fastmcp import FastMCP
from .credentials import CredentialManager
from .config import Config
from .compute import list_vms, get_vm_config
from .network import list_networks, list_subnets, list_security_groups, get_security_group_config
from .storage import list_disks, get_disk_config, list_snapshots, get_snapshot_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Yandex Cloud VM Manager")

# Global credential manager
credentials = CredentialManager()


@mcp.tool()
def setup_credentials(iam_token: str, folder_id: str) -> str:
    """
    Setup Yandex Cloud credentials for the session
    
    Args:
        iam_token: Yandex Cloud IAM token (format: t1.xxxxx...)
        folder_id: Yandex Cloud folder ID (20 character alphanumeric string)
        
    Returns:
        Success or error message
    """
    # Validate inputs
    if not CredentialManager._validate_token(iam_token):
        return f"{Config.CREDENTIALS_ERROR}: Invalid IAM token format. Must start with 't1.' and be longer than 50 characters."
    
    if not CredentialManager._validate_folder_id(folder_id):
        return f"{Config.CREDENTIALS_ERROR}: Invalid folder ID format. Must be 20 character alphanumeric string."
    
    # Test the credentials by trying to create SDK
    try:
        import yandexcloud
        _ = yandexcloud.SDK(iam_token=iam_token)
        credentials.set_credentials(iam_token, folder_id)
        logger.info("Credentials configured successfully")
        return Config.CREDENTIALS_SUCCESS
    except Exception as e:
        logger.error(f"Failed to configure credentials: {str(e)}")
        return f"{Config.CREDENTIALS_ERROR}: {str(e)}"


@mcp.tool()
def get_credentials_status() -> str:
    """
    Check current credentials status
    
    Returns:
        Status of configured credentials
    """
    iam_configured = bool(credentials.get_token())
    folder_configured = bool(credentials.get_folder_id())
    
    status = "🔐 Credentials Status:\n"
    status += f"• IAM Token: {'✅ Configured' if iam_configured else '❌ Not configured'}\n"
    status += f"• Folder ID: {'✅ Configured' if folder_configured else '❌ Not configured'}\n"
    
    if not iam_configured or not folder_configured:
        status += "\n💡 Use setup_credentials(iam_token, folder_id) to configure missing credentials."
        status += "\n\nTo get your credentials:"
        status += "\n• IAM Token: `yc iam create-token`"
        status += "\n• Folder ID: `yc config list`"
    
    return status


@mcp.tool()
def clear_credentials() -> str:
    """
    Clear stored credentials from session
    
    Returns:
        Confirmation message
    """
    credentials.clear()
    logger.info("Credentials cleared")
    return "🗑️ Credentials cleared from session"


# Compute tools
@mcp.tool()
def list_virtual_machines(folder_id: str = None):
    """List all virtual machines"""
    return list_vms(credentials, folder_id)


@mcp.tool()
def get_virtual_machine_config(instance_id: str):
    """Get detailed VM configuration"""
    return get_vm_config(credentials, instance_id)


# Network tools
@mcp.tool()
def list_vpc_networks(folder_id: str = None):
    """List all VPC networks"""
    return list_networks(credentials, folder_id)


@mcp.tool()
def list_vpc_subnets(folder_id: str = None):
    """List all VPC subnets"""
    return list_subnets(credentials, folder_id)


@mcp.tool()
def list_vpc_security_groups(folder_id: str = None):
    """List all security groups"""
    return list_security_groups(credentials, folder_id)


@mcp.tool()
def get_security_group_details(security_group_id: str):
    """Get detailed security group configuration"""
    return get_security_group_config(credentials, security_group_id)


# Storage tools
@mcp.tool()
def list_storage_disks(folder_id: str = None):
    """List all storage disks"""
    return list_disks(credentials, folder_id)


@mcp.tool()
def get_disk_details(disk_id: str):
    """Get detailed disk configuration"""
    return get_disk_config(credentials, disk_id)


@mcp.tool()
def list_disk_snapshots(folder_id: str = None):
    """List all disk snapshots"""
    return list_snapshots(credentials, folder_id)


@mcp.tool()
def get_snapshot_details(snapshot_id: str):
    """Get detailed snapshot configuration"""
    return get_snapshot_config(credentials, snapshot_id)


def main():
    """Main entry point"""
    mcp.run()


if __name__ == "__main__":
    main()