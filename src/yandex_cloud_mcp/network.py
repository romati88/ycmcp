"""
Network service functions for VPC resources
"""

import logging
from typing import List, Dict, Any
from yandex.cloud.vpc.v1.network_service_pb2 import ListNetworksRequest, GetNetworkRequest
from yandex.cloud.vpc.v1.network_service_pb2_grpc import NetworkServiceStub
from yandex.cloud.vpc.v1.subnet_service_pb2 import ListSubnetsRequest, GetSubnetRequest
from yandex.cloud.vpc.v1.subnet_service_pb2_grpc import SubnetServiceStub
from yandex.cloud.vpc.v1.security_group_service_pb2 import ListSecurityGroupsRequest, GetSecurityGroupRequest
from yandex.cloud.vpc.v1.security_group_service_pb2_grpc import SecurityGroupServiceStub
from .credentials import CredentialManager, get_yc_sdk
from .config import Config

logger = logging.getLogger(__name__)


def list_networks(credentials: CredentialManager, folder_id: str = None) -> List[Dict[str, Any]]:
    """List all networks in specified folder"""
    if not folder_id:
        folder_id = credentials.get_folder_id()
        if not folder_id:
            raise ValueError(Config.FOLDER_NOT_CONFIGURED)
    
    try:
        sdk = get_yc_sdk(credentials)
        network_service = sdk.client(NetworkServiceStub)
        
        request = ListNetworksRequest(folder_id=folder_id)
        response = network_service.List(request)
        
        networks = []
        for network in response.networks:
            network_info = {
                "id": network.id,
                "name": network.name,
                "description": network.description,
                "folder_id": network.folder_id,
                "created_at": str(network.created_at) if network.created_at else None,
                "default_security_group_id": network.default_security_group_id,
            }
            networks.append(network_info)
        
        logger.info(f"Retrieved {len(networks)} networks from folder {folder_id}")
        return networks
        
    except Exception as e:
        logger.error(f"Failed to list networks: {str(e)}")
        raise ValueError(f"Failed to retrieve networks: {str(e)}")


def list_subnets(credentials: CredentialManager, folder_id: str = None) -> List[Dict[str, Any]]:
    """List all subnets in specified folder"""
    if not folder_id:
        folder_id = credentials.get_folder_id()
        if not folder_id:
            raise ValueError(Config.FOLDER_NOT_CONFIGURED)
    
    try:
        sdk = get_yc_sdk(credentials)
        subnet_service = sdk.client(SubnetServiceStub)
        
        request = ListSubnetsRequest(folder_id=folder_id)
        response = subnet_service.List(request)
        
        subnets = []
        for subnet in response.subnets:
            subnet_info = {
                "id": subnet.id,
                "name": subnet.name,
                "description": subnet.description,
                "folder_id": subnet.folder_id,
                "network_id": subnet.network_id,
                "zone_id": subnet.zone_id,
                "v4_cidr_blocks": list(subnet.v4_cidr_blocks),
                "v6_cidr_blocks": list(subnet.v6_cidr_blocks),
                "route_table_id": subnet.route_table_id,
                "created_at": str(subnet.created_at) if subnet.created_at else None,
            }
            subnets.append(subnet_info)
        
        logger.info(f"Retrieved {len(subnets)} subnets from folder {folder_id}")
        return subnets
        
    except Exception as e:
        logger.error(f"Failed to list subnets: {str(e)}")
        raise ValueError(f"Failed to retrieve subnets: {str(e)}")


def list_security_groups(credentials: CredentialManager, folder_id: str = None) -> List[Dict[str, Any]]:
    """List all security groups in specified folder"""
    if not folder_id:
        folder_id = credentials.get_folder_id()
        if not folder_id:
            raise ValueError(Config.FOLDER_NOT_CONFIGURED)
    
    try:
        sdk = get_yc_sdk(credentials)
        sg_service = sdk.client(SecurityGroupServiceStub)
        
        request = ListSecurityGroupsRequest(folder_id=folder_id)
        response = sg_service.List(request)
        
        security_groups = []
        for sg in response.security_groups:
            sg_info = {
                "id": sg.id,
                "name": sg.name,
                "description": sg.description,
                "folder_id": sg.folder_id,
                "network_id": sg.network_id,
                "status": str(sg.status),
                "rules_count": len(sg.rules),
                "created_at": str(sg.created_at) if sg.created_at else None,
            }
            security_groups.append(sg_info)
        
        logger.info(f"Retrieved {len(security_groups)} security groups from folder {folder_id}")
        return security_groups
        
    except Exception as e:
        logger.error(f"Failed to list security groups: {str(e)}")
        raise ValueError(f"Failed to retrieve security groups: {str(e)}")


def get_security_group_config(credentials: CredentialManager, security_group_id: str) -> Dict[str, Any]:
    """Get detailed configuration of a specific security group"""
    try:
        sdk = get_yc_sdk(credentials)
        sg_service = sdk.client(SecurityGroupServiceStub)
        
        request = GetSecurityGroupRequest(security_group_id=security_group_id)
        sg = sg_service.Get(request)
        
        # Extract rules
        rules = []
        for rule in sg.rules:
            rule_info = {
                "id": rule.id,
                "description": rule.description,
                "direction": str(rule.direction),
                "protocol_name": rule.protocol_name,
                "protocol_number": rule.protocol_number,
                "port_range": {
                    "from_port": rule.ports.from_port if rule.ports else None,
                    "to_port": rule.ports.to_port if rule.ports else None,
                },
            }
            
            # Add target information
            if rule.cidr_blocks:
                rule_info["cidr_blocks"] = {
                    "v4_cidr_blocks": list(rule.cidr_blocks.v4_cidr_blocks),
                    "v6_cidr_blocks": list(rule.cidr_blocks.v6_cidr_blocks),
                }
            elif rule.security_group_id:
                rule_info["security_group_id"] = rule.security_group_id
            elif rule.predefined_target:
                rule_info["predefined_target"] = rule.predefined_target
            
            rules.append(rule_info)
        
        sg_config = {
            "id": sg.id,
            "name": sg.name,
            "description": sg.description,
            "folder_id": sg.folder_id,
            "network_id": sg.network_id,
            "status": str(sg.status),
            "created_at": str(sg.created_at) if sg.created_at else None,
            "rules": rules,
            "default_for_network": sg.default_for_network,
        }
        
        logger.info(f"Retrieved security group config for {security_group_id}")
        return sg_config
        
    except Exception as e:
        logger.error(f"Failed to get security group config: {str(e)}")
        raise ValueError(f"Failed to retrieve security group configuration: {str(e)}")