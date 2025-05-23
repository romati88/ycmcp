"""
Resource Manager service functions for cloud and organization level operations
"""

import logging
from typing import List, Dict, Any, Optional
from yandex.cloud.resourcemanager.v1.cloud_service_pb2 import ListCloudsRequest, GetCloudRequest
from yandex.cloud.resourcemanager.v1.cloud_service_pb2_grpc import CloudServiceStub
from yandex.cloud.resourcemanager.v1.folder_service_pb2 import ListFoldersRequest, GetFolderRequest
from yandex.cloud.resourcemanager.v1.folder_service_pb2_grpc import FolderServiceStub
from .credentials import CredentialManager, get_yc_sdk
from .config import Config

logger = logging.getLogger(__name__)


def list_clouds(credentials: CredentialManager, organization_id: str = None) -> List[Dict[str, Any]]:
    """
    List all clouds in organization (if organization_id provided) or all accessible clouds
    
    Args:
        credentials: Credential manager instance
        organization_id: Organization ID (optional)
        
    Returns:
        List of clouds with basic information
    """
    try:
        sdk = get_yc_sdk(credentials)
        cloud_service = sdk.client(CloudServiceStub)
        
        request = ListCloudsRequest()
        if organization_id:
            request.organization_id = organization_id
            
        response = cloud_service.List(request)
        
        clouds = []
        for cloud in response.clouds:
            cloud_info = {
                "id": cloud.id,
                "name": cloud.name,
                "description": cloud.description,
                "organization_id": cloud.organization_id,
                "created_at": str(cloud.created_at) if cloud.created_at else None,
            }
            clouds.append(cloud_info)
        
        logger.info(f"Retrieved {len(clouds)} clouds")
        return clouds
        
    except Exception as e:
        logger.error(f"Failed to list clouds: {str(e)}")
        raise ValueError(f"Failed to retrieve clouds: {str(e)}")


def get_cloud_details(credentials: CredentialManager, cloud_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific cloud
    
    Args:
        credentials: Credential manager instance
        cloud_id: Cloud ID
        
    Returns:
        Detailed cloud information
    """
    try:
        sdk = get_yc_sdk(credentials)
        cloud_service = sdk.client(CloudServiceStub)
        
        request = GetCloudRequest(cloud_id=cloud_id)
        cloud = cloud_service.Get(request)
        
        cloud_info = {
            "id": cloud.id,
            "name": cloud.name,
            "description": cloud.description,
            "organization_id": cloud.organization_id,
            "created_at": str(cloud.created_at) if cloud.created_at else None,
        }
        
        logger.info(f"Retrieved cloud details for {cloud_id}")
        return cloud_info
        
    except Exception as e:
        logger.error(f"Failed to get cloud details: {str(e)}")
        raise ValueError(f"Failed to retrieve cloud details: {str(e)}")


def list_folders(credentials: CredentialManager, cloud_id: str = None) -> List[Dict[str, Any]]:
    """
    List all folders in specified cloud
    
    Args:
        credentials: Credential manager instance
        cloud_id: Cloud ID (if not provided, will prompt user to select from available clouds)
        
    Returns:
        List of folders with basic information
    """
    try:
        sdk = get_yc_sdk(credentials)
        folder_service = sdk.client(FolderServiceStub)
        
        # If no cloud_id provided, help user select one
        if not cloud_id:
            clouds = list_clouds(credentials)
            if not clouds:
                raise ValueError("No clouds found. Please check your permissions.")
            
            if len(clouds) == 1:
                cloud_id = clouds[0]["id"]
                logger.info(f"Auto-selected cloud: {clouds[0]['name']} ({cloud_id})")
            else:
                # Return available clouds for user selection
                clouds_info = {
                    "error": "cloud_id_required",
                    "message": "Please specify cloud_id. Available clouds:",
                    "available_clouds": [
                        {
                            "id": cloud["id"],
                            "name": cloud["name"],
                            "organization_id": cloud.get("organization_id")
                        }
                        for cloud in clouds
                    ],
                    "suggestion": f"Use: list_yandex_folders(cloud_id='{clouds[0]['id']}')"
                }
                return [clouds_info]
        
        request = ListFoldersRequest(cloud_id=cloud_id)
        response = folder_service.List(request)
        
        folders = []
        for folder in response.folders:
            folder_info = {
                "id": folder.id,
                "name": folder.name,
                "description": folder.description,
                "cloud_id": folder.cloud_id,
                "status": str(folder.status),
                "created_at": str(folder.created_at) if folder.created_at else None,
            }
            folders.append(folder_info)
        
        logger.info(f"Retrieved {len(folders)} folders from cloud {cloud_id}")
        return folders
        
    except Exception as e:
        logger.error(f"Failed to list folders: {str(e)}")
        if "cloud_id: Field is required" in str(e):
            # Try to get available clouds for user
            try:
                clouds = list_clouds(credentials)
                clouds_info = {
                    "error": "cloud_id_required",
                    "message": "cloud_id is required for listing folders. Available clouds:",
                    "available_clouds": [
                        {
                            "id": cloud["id"],
                            "name": cloud["name"],
                            "organization_id": cloud.get("organization_id")
                        }
                        for cloud in clouds
                    ]
                }
                if clouds:
                    clouds_info["suggestion"] = f"Use: list_yandex_folders(cloud_id='{clouds[0]['id']}')"
                return [clouds_info]
            except:
                pass
        raise ValueError(f"Failed to retrieve folders: {str(e)}")


def get_folder_details(credentials: CredentialManager, folder_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific folder
    
    Args:
        credentials: Credential manager instance
        folder_id: Folder ID
        
    Returns:
        Detailed folder information
    """
    try:
        sdk = get_yc_sdk(credentials)
        folder_service = sdk.client(FolderServiceStub)
        
        request = GetFolderRequest(folder_id=folder_id)
        folder = folder_service.Get(request)
        
        folder_info = {
            "id": folder.id,
            "name": folder.name,
            "description": folder.description,
            "cloud_id": folder.cloud_id,
            "status": str(folder.status),
            "created_at": str(folder.created_at) if folder.created_at else None,
        }
        
        logger.info(f"Retrieved folder details for {folder_id}")
        return folder_info
        
    except Exception as e:
        logger.error(f"Failed to get folder details: {str(e)}")
        raise ValueError(f"Failed to retrieve folder details: {str(e)}")


def get_organization_context(credentials: CredentialManager) -> Dict[str, Any]:
    """
    Get organization context with available clouds and folders
    
    Args:
        credentials: Credential manager instance
        
    Returns:
        Organization context with hierarchy information
    """
    try:
        context = {
            "clouds": [],
            "total_folders": 0,
            "organization_id": None
        }
        
        # Get all accessible clouds
        clouds = list_clouds(credentials)
        
        for cloud in clouds:
            cloud_info = {
                "id": cloud["id"],
                "name": cloud["name"],
                "organization_id": cloud.get("organization_id"),
                "folders": []
            }
            
            # Get folders for this cloud
            try:
                folders = list_folders(credentials, cloud["id"])
                # Skip error responses
                if isinstance(folders, list) and folders and not folders[0].get("error"):
                    cloud_info["folders"] = folders
                    context["total_folders"] += len(folders)
            except Exception as e:
                logger.warning(f"Could not get folders for cloud {cloud['id']}: {e}")
            
            context["clouds"].append(cloud_info)
            
            # Set organization_id from first cloud
            if not context["organization_id"] and cloud.get("organization_id"):
                context["organization_id"] = cloud["organization_id"]
        
        return context
        
    except Exception as e:
        logger.error(f"Failed to get organization context: {str(e)}")
        raise ValueError(f"Failed to retrieve organization context: {str(e)}")


def suggest_scope_for_query(credentials: CredentialManager, resource_type: str) -> Dict[str, Any]:
    """
    Suggest appropriate scope (folder/cloud/organization) for resource queries
    
    Args:
        credentials: Credential manager instance
        resource_type: Type of resource being queried (vms, networks, etc.)
        
    Returns:
        Scope suggestions with available IDs
    """
    try:
        context = get_organization_context(credentials)
        
        suggestions = {
            "resource_type": resource_type,
            "configured_folder_id": credentials.get_folder_id(),
            "available_scopes": {
                "folder": {
                    "description": "Query resources in a specific folder (default scope)",
                    "current": credentials.get_folder_id(),
                    "available_folders": []
                },
                "cloud": {
                    "description": "Query resources across all folders in a cloud",
                    "available_clouds": [
                        {"id": cloud["id"], "name": cloud["name"]}
                        for cloud in context["clouds"]
                    ]
                },
                "organization": {
                    "description": "Query resources across all clouds in organization",
                    "organization_id": context["organization_id"]
                }
            },
            "recommendations": []
        }
        
        # Collect all folders from all clouds
        for cloud in context["clouds"]:
            for folder in cloud.get("folders", []):
                suggestions["available_scopes"]["folder"]["available_folders"].append({
                    "id": folder["id"],
                    "name": folder["name"],
                    "cloud_id": folder["cloud_id"],
                    "cloud_name": next((c["name"] for c in context["clouds"] if c["id"] == folder["cloud_id"]), "Unknown")
                })
        
        # Add recommendations based on resource type
        if resource_type in ["vms", "disks", "snapshots", "images"]:
            suggestions["recommendations"].append("For compute resources, folder scope is usually sufficient")
        elif resource_type in ["networks", "subnets", "security_groups"]:
            suggestions["recommendations"].append("For network resources, consider cloud scope to see cross-folder connectivity")
        elif resource_type in ["zones", "disk_types"]:
            suggestions["recommendations"].append("For infrastructure resources, organization scope shows all available options")
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Failed to suggest scope: {str(e)}")
        raise ValueError(f"Failed to suggest scope: {str(e)}")