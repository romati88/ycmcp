"""
Storage service functions for disks and snapshots
"""

import logging
from typing import List, Dict, Any
from yandex.cloud.compute.v1.disk_service_pb2 import ListDisksRequest, GetDiskRequest
from yandex.cloud.compute.v1.disk_service_pb2_grpc import DiskServiceStub
from yandex.cloud.compute.v1.snapshot_service_pb2 import ListSnapshotsRequest, GetSnapshotRequest
from yandex.cloud.compute.v1.snapshot_service_pb2_grpc import SnapshotServiceStub
from .credentials import CredentialManager, get_yc_sdk
from .config import Config

logger = logging.getLogger(__name__)


def list_disks(credentials: CredentialManager, folder_id: str = None) -> List[Dict[str, Any]]:
    """List all disks in specified folder"""
    if not folder_id:
        folder_id = credentials.get_folder_id()
        if not folder_id:
            raise ValueError(Config.FOLDER_NOT_CONFIGURED)
    
    try:
        sdk = get_yc_sdk(credentials)
        disk_service = sdk.client(DiskServiceStub)
        
        request = ListDisksRequest(folder_id=folder_id)
        response = disk_service.List(request)
        
        disks = []
        for disk in response.disks:
            disk_info = {
                "id": disk.id,
                "name": disk.name,
                "description": disk.description,
                "folder_id": disk.folder_id,
                "size": disk.size,
                "block_size": disk.block_size,
                "product_ids": list(disk.product_ids),
                "status": str(disk.status),
                "source_type": str(disk.source_image_id) if disk.source_image_id else (
                    str(disk.source_snapshot_id) if disk.source_snapshot_id else "none"
                ),
                "instance_ids": list(disk.instance_ids),
                "disk_placement_policy": {
                    "placement_group_id": disk.disk_placement_policy.placement_group_id if disk.disk_placement_policy else None,
                },
                "type_id": disk.type_id,
                "zone_id": disk.zone_id,
                "created_at": str(disk.created_at) if disk.created_at else None,
            }
            disks.append(disk_info)
        
        logger.info(f"Retrieved {len(disks)} disks from folder {folder_id}")
        return disks
        
    except Exception as e:
        logger.error(f"Failed to list disks: {str(e)}")
        raise ValueError(f"Failed to retrieve disks: {str(e)}")


def get_disk_config(credentials: CredentialManager, disk_id: str) -> Dict[str, Any]:
    """Get detailed configuration of a specific disk"""
    try:
        sdk = get_yc_sdk(credentials)
        disk_service = sdk.client(DiskServiceStub)
        
        request = GetDiskRequest(disk_id=disk_id)
        disk = disk_service.Get(request)
        
        disk_config = {
            "id": disk.id,
            "name": disk.name,
            "description": disk.description,
            "folder_id": disk.folder_id,
            "size": disk.size,
            "block_size": disk.block_size,
            "product_ids": list(disk.product_ids),
            "status": str(disk.status),
            "source_image_id": disk.source_image_id,
            "source_snapshot_id": disk.source_snapshot_id,
            "instance_ids": list(disk.instance_ids),
            "disk_placement_policy": {
                "placement_group_id": disk.disk_placement_policy.placement_group_id if disk.disk_placement_policy else None,
                "placement_group_partition": disk.disk_placement_policy.placement_group_partition if disk.disk_placement_policy else None,
            },
            "type_id": disk.type_id,
            "zone_id": disk.zone_id,
            "created_at": str(disk.created_at) if disk.created_at else None,
            "labels": dict(disk.labels),
        }
        
        logger.info(f"Retrieved disk config for {disk_id}")
        return disk_config
        
    except Exception as e:
        logger.error(f"Failed to get disk config: {str(e)}")
        raise ValueError(f"Failed to retrieve disk configuration: {str(e)}")


def list_snapshots(credentials: CredentialManager, folder_id: str = None) -> List[Dict[str, Any]]:
    """List all snapshots in specified folder"""
    if not folder_id:
        folder_id = credentials.get_folder_id()
        if not folder_id:
            raise ValueError(Config.FOLDER_NOT_CONFIGURED)
    
    try:
        sdk = get_yc_sdk(credentials)
        snapshot_service = sdk.client(SnapshotServiceStub)
        
        request = ListSnapshotsRequest(folder_id=folder_id)
        response = snapshot_service.List(request)
        
        snapshots = []
        for snapshot in response.snapshots:
            snapshot_info = {
                "id": snapshot.id,
                "name": snapshot.name,
                "description": snapshot.description,
                "folder_id": snapshot.folder_id,
                "storage_size": snapshot.storage_size,
                "disk_size": snapshot.disk_size,
                "product_ids": list(snapshot.product_ids),
                "status": str(snapshot.status),
                "source_disk_id": snapshot.source_disk_id,
                "created_at": str(snapshot.created_at) if snapshot.created_at else None,
            }
            snapshots.append(snapshot_info)
        
        logger.info(f"Retrieved {len(snapshots)} snapshots from folder {folder_id}")
        return snapshots
        
    except Exception as e:
        logger.error(f"Failed to list snapshots: {str(e)}")
        raise ValueError(f"Failed to retrieve snapshots: {str(e)}")


def get_snapshot_config(credentials: CredentialManager, snapshot_id: str) -> Dict[str, Any]:
    """Get detailed configuration of a specific snapshot"""
    try:
        sdk = get_yc_sdk(credentials)
        snapshot_service = sdk.client(SnapshotServiceStub)
        
        request = GetSnapshotRequest(snapshot_id=snapshot_id)
        snapshot = snapshot_service.Get(request)
        
        snapshot_config = {
            "id": snapshot.id,
            "name": snapshot.name,
            "description": snapshot.description,
            "folder_id": snapshot.folder_id,
            "storage_size": snapshot.storage_size,
            "disk_size": snapshot.disk_size,
            "product_ids": list(snapshot.product_ids),
            "status": str(snapshot.status),
            "source_disk_id": snapshot.source_disk_id,
            "created_at": str(snapshot.created_at) if snapshot.created_at else None,
            "labels": dict(snapshot.labels),
        }
        
        logger.info(f"Retrieved snapshot config for {snapshot_id}")
        return snapshot_config
        
    except Exception as e:
        logger.error(f"Failed to get snapshot config: {str(e)}")
        raise ValueError(f"Failed to retrieve snapshot configuration: {str(e)}")