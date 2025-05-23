"""
Compute service functions for VMs
"""

import logging
from typing import List, Dict, Any
from yandex.cloud.compute.v1.instance_service_pb2 import ListInstancesRequest, GetInstanceRequest
from yandex.cloud.compute.v1.instance_service_pb2_grpc import InstanceServiceStub
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