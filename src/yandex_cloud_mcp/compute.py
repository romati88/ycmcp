"""
Compute service functions for VMs and related resources
"""

import logging
from typing import List, Dict, Any
from yandex.cloud.compute.v1.instance_service_pb2 import ListInstancesRequest, GetInstanceRequest
from yandex.cloud.compute.v1.instance_service_pb2_grpc import InstanceServiceStub
from yandex.cloud.compute.v1.image_service_pb2 import ListImagesRequest, GetImageRequest
from yandex.cloud.compute.v1.image_service_pb2_grpc import ImageServiceStub
from yandex.cloud.compute.v1.disk_service_pb2 import ListDisksRequest, GetDiskRequest
from yandex.cloud.compute.v1.disk_service_pb2_grpc import DiskServiceStub
from yandex.cloud.compute.v1.snapshot_service_pb2 import ListSnapshotsRequest, GetSnapshotRequest
from yandex.cloud.compute.v1.snapshot_service_pb2_grpc import SnapshotServiceStub
from yandex.cloud.compute.v1.zone_service_pb2 import ListZonesRequest, GetZoneRequest
from yandex.cloud.compute.v1.zone_service_pb2_grpc import ZoneServiceStub
from yandex.cloud.compute.v1.disk_type_service_pb2 import ListDiskTypesRequest, GetDiskTypeRequest
from yandex.cloud.compute.v1.disk_type_service_pb2_grpc import DiskTypeServiceStub
from .credentials import CredentialManager, get_yc_sdk
from .config import Config

logger = logging.getLogger(__name__)


def list_vms(credentials: CredentialManager, folder_id: str = None) -> List[Dict[str, Any]]:
    """
    List all virtual machines in specified folder
    
    Args:
        credentials: Credential manager instance
        folder_id: Yandex Cloud folder ID (optional, will use configured folder_id if not provided)
        
    Returns:
        List of VM instances with basic information
        
    Raises:
        ValueError: If folder_id is not provided and not configured
    """
    if not folder_id:
        folder_id = credentials.get_folder_id()
        if not folder_id:
            raise ValueError(Config.FOLDER_NOT_CONFIGURED)
    
    try:
        sdk = get_yc_sdk(credentials)
        instance_service = sdk.client(InstanceServiceStub)
        
        request = ListInstancesRequest(folder_id=folder_id)
        response = instance_service.List(request)
        
        vms = []
        for instance in response.instances:
            vm_info = {
                "id": instance.id,
                "name": instance.name,
                "description": instance.description,
                "status": str(instance.status),
                "zone_id": instance.zone_id,
                "platform_id": instance.platform_id,
                "created_at": str(instance.created_at) if instance.created_at else None,
            }
            vms.append(vm_info)
        
        logger.info(f"Retrieved {len(vms)} VMs from folder {folder_id}")
        return vms
        
    except Exception as e:
        logger.error(f"Failed to list VMs: {str(e)}")
        raise ValueError(f"Failed to retrieve VM list: {str(e)}")


def get_vm_config(credentials: CredentialManager, instance_id: str) -> Dict[str, Any]:
    """
    Get detailed configuration of a specific virtual machine
    
    Args:
        credentials: Credential manager instance
        instance_id: VM instance ID
        
    Returns:
        Detailed VM configuration including resources and network settings
    """
    try:
        sdk = get_yc_sdk(credentials)
        instance_service = sdk.client(InstanceServiceStub)
        
        request = GetInstanceRequest(instance_id=instance_id)
        instance = instance_service.Get(request)
        
        # Extract network interfaces info
        network_interfaces = []
        for ni in instance.network_interfaces:
            interface_info = {
                "index": ni.index,
                "mac_address": ni.mac_address,
                "subnet_id": ni.subnet_id,
                "primary_v4_address": ni.primary_v4_address.address if ni.primary_v4_address else None,
                "primary_v6_address": ni.primary_v6_address.address if ni.primary_v6_address else None,
            }
            # Add public IP if available
            if ni.primary_v4_address and ni.primary_v4_address.one_to_one_nat:
                interface_info["public_ip"] = ni.primary_v4_address.one_to_one_nat.address
            
            network_interfaces.append(interface_info)
        
        # Extract boot disk info
        boot_disk = None
        if instance.boot_disk:
            boot_disk = {
                "disk_id": instance.boot_disk.disk_id,
                "auto_delete": instance.boot_disk.auto_delete,
                "device_name": instance.boot_disk.device_name,
            }
        
        # Extract secondary disks info
        secondary_disks = []
        for disk in instance.secondary_disks:
            disk_info = {
                "disk_id": disk.disk_id,
                "auto_delete": disk.auto_delete,
                "device_name": disk.device_name,
            }
            secondary_disks.append(disk_info)
        
        vm_config = {
            "id": instance.id,
            "name": instance.name,
            "description": instance.description,
            "status": str(instance.status),
            "zone_id": instance.zone_id,
            "platform_id": instance.platform_id,
            "folder_id": instance.folder_id,
            "created_at": str(instance.created_at) if instance.created_at else None,
            "fqdn": instance.fqdn,
            "resources": {
                "cores": instance.resources.cores,
                "memory": instance.resources.memory,
                "core_fraction": instance.resources.core_fraction,
                "gpus": instance.resources.gpus,
            },
            "metadata": dict(instance.metadata),
            "network_interfaces": network_interfaces,
            "boot_disk": boot_disk,
            "secondary_disks": secondary_disks,
            "service_account_id": instance.service_account_id,
            "network_settings": {
                "type": str(instance.network_settings.type) if instance.network_settings else "STANDARD",
            },
            "placement_policy": {
                "placement_group_id": instance.placement_policy.placement_group_id if instance.placement_policy else None,
                "host_affinity_rules": list(instance.placement_policy.host_affinity_rules) if instance.placement_policy else [],
            },
            "scheduling_policy": {
                "preemptible": instance.scheduling_policy.preemptible if instance.scheduling_policy else False,
            },
        }
        
        logger.info(f"Retrieved VM config for {instance_id}")
        return vm_config
        
    except Exception as e:
        logger.error(f"Failed to get VM config: {str(e)}")
        raise ValueError(f"Failed to retrieve VM configuration: {str(e)}")


def list_images(credentials: CredentialManager, folder_id: str = None) -> List[Dict[str, Any]]:
    """
    List all images in specified folder
    
    Args:
        credentials: Credential manager instance
        folder_id: Yandex Cloud folder ID (optional, will use configured folder_id if not provided)
        
    Returns:
        List of images with basic information
    """
    if not folder_id:
        folder_id = credentials.get_folder_id()
        if not folder_id:
            raise ValueError(Config.FOLDER_NOT_CONFIGURED)
    
    try:
        sdk = get_yc_sdk(credentials)
        image_service = sdk.client(ImageServiceStub)
        
        request = ListImagesRequest(folder_id=folder_id)
        response = image_service.List(request)
        
        images = []
        for image in response.images:
            image_info = {
                "id": image.id,
                "name": image.name,
                "description": image.description,
                "family": image.family,
                "storage_size": image.storage_size,
                "min_disk_size": image.min_disk_size,
                "product_ids": list(image.product_ids),
                "status": str(image.status),
                "os": {
                    "type": str(image.os.type) if image.os else None,
                },
                "created_at": str(image.created_at) if image.created_at else None,
            }
            images.append(image_info)
        
        logger.info(f"Retrieved {len(images)} images from folder {folder_id}")
        return images
        
    except Exception as e:
        logger.error(f"Failed to list images: {str(e)}")
        raise ValueError(f"Failed to retrieve images: {str(e)}")


def get_image_details(credentials: CredentialManager, image_id: str) -> Dict[str, Any]:
    """
    Get detailed configuration of a specific image
    
    Args:
        credentials: Credential manager instance
        image_id: Image ID
        
    Returns:
        Detailed image configuration
    """
    try:
        sdk = get_yc_sdk(credentials)
        image_service = sdk.client(ImageServiceStub)
        
        request = GetImageRequest(image_id=image_id)
        image = image_service.Get(request)
        
        image_config = {
            "id": image.id,
            "name": image.name,
            "description": image.description,
            "folder_id": image.folder_id,
            "family": image.family,
            "storage_size": image.storage_size,
            "min_disk_size": image.min_disk_size,
            "product_ids": list(image.product_ids),
            "status": str(image.status),
            "os": {
                "type": str(image.os.type) if image.os else None,
            },
            "pooled": image.pooled,
            "created_at": str(image.created_at) if image.created_at else None,
        }
        
        logger.info(f"Retrieved image config for {image_id}")
        return image_config
        
    except Exception as e:
        logger.error(f"Failed to get image config: {str(e)}")
        raise ValueError(f"Failed to retrieve image configuration: {str(e)}")


def list_zones(credentials: CredentialManager) -> List[Dict[str, Any]]:
    """
    List all availability zones
    
    Args:
        credentials: Credential manager instance
        
    Returns:
        List of availability zones
    """
    try:
        sdk = get_yc_sdk(credentials)
        zone_service = sdk.client(ZoneServiceStub)
        
        request = ListZonesRequest()
        response = zone_service.List(request)
        
        zones = []
        for zone in response.zones:
            zone_info = {
                "id": zone.id,
                "region_id": zone.region_id,
                "status": str(zone.status),
            }
            zones.append(zone_info)
        
        logger.info(f"Retrieved {len(zones)} zones")
        return zones
        
    except Exception as e:
        logger.error(f"Failed to list zones: {str(e)}")
        raise ValueError(f"Failed to retrieve zones: {str(e)}")


def get_zone_details(credentials: CredentialManager, zone_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific zone
    
    Args:
        credentials: Credential manager instance
        zone_id: Zone ID
        
    Returns:
        Detailed zone information
    """
    try:
        sdk = get_yc_sdk(credentials)
        zone_service = sdk.client(ZoneServiceStub)
        
        request = GetZoneRequest(zone_id=zone_id)
        zone = zone_service.Get(request)
        
        zone_info = {
            "id": zone.id,
            "region_id": zone.region_id,
            "status": str(zone.status),
        }
        
        logger.info(f"Retrieved zone details for {zone_id}")
        return zone_info
        
    except Exception as e:
        logger.error(f"Failed to get zone details: {str(e)}")
        raise ValueError(f"Failed to retrieve zone details: {str(e)}")


def list_disk_types(credentials: CredentialManager, zone_id: str = None) -> List[Dict[str, Any]]:
    """
    List all disk types in specified zone or all zones
    
    Args:
        credentials: Credential manager instance
        zone_id: Zone ID (optional)
        
    Returns:
        List of disk types
    """
    try:
        sdk = get_yc_sdk(credentials)
        disk_type_service = sdk.client(DiskTypeServiceStub)
        
        request = ListDiskTypesRequest()
        if zone_id:
            request.zone_id = zone_id
            
        response = disk_type_service.List(request)
        
        disk_types = []
        for disk_type in response.disk_types:
            disk_type_info = {
                "id": disk_type.id,
                "description": disk_type.description,
                "zone_ids": list(disk_type.zone_ids),
            }
            disk_types.append(disk_type_info)
        
        logger.info(f"Retrieved {len(disk_types)} disk types")
        return disk_types
        
    except Exception as e:
        logger.error(f"Failed to list disk types: {str(e)}")
        raise ValueError(f"Failed to retrieve disk types: {str(e)}")


def get_disk_type_details(credentials: CredentialManager, disk_type_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific disk type
    
    Args:
        credentials: Credential manager instance
        disk_type_id: Disk type ID
        
    Returns:
        Detailed disk type information
    """
    try:
        sdk = get_yc_sdk(credentials)
        disk_type_service = sdk.client(DiskTypeServiceStub)
        
        request = GetDiskTypeRequest(disk_type_id=disk_type_id)
        disk_type = disk_type_service.Get(request)
        
        disk_type_info = {
            "id": disk_type.id,
            "description": disk_type.description,
            "zone_ids": list(disk_type.zone_ids),
        }
        
        logger.info(f"Retrieved disk type details for {disk_type_id}")
        return disk_type_info
        
    except Exception as e:
        logger.error(f"Failed to get disk type details: {str(e)}")
        raise ValueError(f"Failed to retrieve disk type details: {str(e)}")