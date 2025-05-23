#!/usr/bin/env python3
"""
Main MCP server implementation
"""

import logging
from fastmcp import FastMCP
from .credentials import CredentialManager
from .config import Config
from .compute import (
    list_vms, get_vm_config, list_images, get_image_details, 
    list_zones, get_zone_details, list_disk_types, get_disk_type_details
)
from .network import (
    list_networks, list_subnets, list_security_groups, get_security_group_config,
    get_network_details, get_subnet_details, list_route_tables, get_route_table_details,
    list_addresses, get_address_details, list_gateways, get_gateway_details
)
from .storage import list_disks, get_disk_config, list_snapshots, get_snapshot_config
from .resource_manager import (
    list_clouds, get_cloud_details, list_folders, get_folder_details,
    get_organization_context, suggest_scope_for_query
)

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


# Resource Manager tools (Cloud/Organization level)
@mcp.tool()
def list_yandex_clouds(organization_id: str = None):
    """List all clouds in organization or all accessible clouds"""
    return list_clouds(credentials, organization_id)


@mcp.tool()
def get_cloud_details_info(cloud_id: str):
    """Get detailed information about a specific cloud"""
    return get_cloud_details(credentials, cloud_id)


@mcp.tool()
def list_yandex_folders(cloud_id: str = None):
    """List all folders in specified cloud or all accessible folders"""
    return list_folders(credentials, cloud_id)


@mcp.tool()
def get_folder_details_info(folder_id: str):
    """Get detailed information about a specific folder"""
    return get_folder_details(credentials, folder_id)


# Extended Compute tools
@mcp.tool()
def list_compute_images(folder_id: str = None):
    """List all images in specified folder"""
    return list_images(credentials, folder_id)


@mcp.tool()
def get_image_configuration(image_id: str):
    """Get detailed configuration of a specific image"""
    return get_image_details(credentials, image_id)


@mcp.tool()
def list_availability_zones():
    """List all availability zones"""
    return list_zones(credentials)


@mcp.tool()
def get_zone_configuration(zone_id: str):
    """Get detailed information about a specific zone"""
    return get_zone_details(credentials, zone_id)


@mcp.tool()
def list_compute_disk_types(zone_id: str = None):
    """List all disk types in specified zone or all zones"""
    return list_disk_types(credentials, zone_id)


@mcp.tool()
def get_disk_type_configuration(disk_type_id: str):
    """Get detailed information about a specific disk type"""
    return get_disk_type_details(credentials, disk_type_id)


# Extended VPC Network tools
@mcp.tool()
def get_network_configuration(network_id: str):
    """Get detailed configuration of a specific network"""
    return get_network_details(credentials, network_id)


@mcp.tool()
def get_subnet_configuration(subnet_id: str):
    """Get detailed configuration of a specific subnet"""
    return get_subnet_details(credentials, subnet_id)


@mcp.tool()
def list_vpc_route_tables(folder_id: str = None):
    """List all route tables in specified folder"""
    return list_route_tables(credentials, folder_id)


@mcp.tool()
def get_route_table_configuration(route_table_id: str):
    """Get detailed configuration of a specific route table"""
    return get_route_table_details(credentials, route_table_id)


@mcp.tool()
def list_vpc_addresses(folder_id: str = None):
    """List all static IP addresses in specified folder"""
    return list_addresses(credentials, folder_id)


@mcp.tool()
def get_address_configuration(address_id: str):
    """Get detailed configuration of a specific static IP address"""
    return get_address_details(credentials, address_id)


@mcp.tool()
def list_vpc_gateways(folder_id: str = None):
    """List all gateways in specified folder"""
    return list_gateways(credentials, folder_id)


@mcp.tool()
def get_gateway_configuration(gateway_id: str):
    """Get detailed configuration of a specific gateway"""
    return get_gateway_details(credentials, gateway_id)


# Helper tools for scope selection
@mcp.tool()
def get_yandex_organization_context():
    """Get organization context with available clouds and folders hierarchy"""
    return get_organization_context(credentials)


@mcp.tool()
def suggest_query_scope(resource_type: str):
    """Suggest appropriate scope (folder/cloud/organization) for resource queries
    
    Args:
        resource_type: Type of resource (vms, networks, disks, etc.)
    """
    return suggest_scope_for_query(credentials, resource_type)


def main():
    """Main entry point"""
    mcp.run()


if __name__ == "__main__":
    main()