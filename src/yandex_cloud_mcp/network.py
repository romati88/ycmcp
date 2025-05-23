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
from yandex.cloud.vpc.v1.route_table_service_pb2 import ListRouteTablesRequest, GetRouteTableRequest
from yandex.cloud.vpc.v1.route_table_service_pb2_grpc import RouteTableServiceStub
from yandex.cloud.vpc.v1.address_service_pb2 import ListAddressesRequest, GetAddressRequest
from yandex.cloud.vpc.v1.address_service_pb2_grpc import AddressServiceStub
from yandex.cloud.vpc.v1.gateway_service_pb2 import ListGatewaysRequest, GetGatewayRequest
from yandex.cloud.vpc.v1.gateway_service_pb2_grpc import GatewayServiceStub
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


def get_network_details(credentials: CredentialManager, network_id: str) -> Dict[str, Any]:
    """Get detailed configuration of a specific network"""
    try:
        sdk = get_yc_sdk(credentials)
        network_service = sdk.client(NetworkServiceStub)
        
        request = GetNetworkRequest(network_id=network_id)
        network = network_service.Get(request)
        
        network_config = {
            "id": network.id,
            "name": network.name,
            "description": network.description,
            "folder_id": network.folder_id,
            "created_at": str(network.created_at) if network.created_at else None,
            "default_security_group_id": network.default_security_group_id,
        }
        
        logger.info(f"Retrieved network config for {network_id}")
        return network_config
        
    except Exception as e:
        logger.error(f"Failed to get network config: {str(e)}")
        raise ValueError(f"Failed to retrieve network configuration: {str(e)}")


def get_subnet_details(credentials: CredentialManager, subnet_id: str) -> Dict[str, Any]:
    """Get detailed configuration of a specific subnet"""
    try:
        sdk = get_yc_sdk(credentials)
        subnet_service = sdk.client(SubnetServiceStub)
        
        request = GetSubnetRequest(subnet_id=subnet_id)
        subnet = subnet_service.Get(request)
        
        subnet_config = {
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
        
        logger.info(f"Retrieved subnet config for {subnet_id}")
        return subnet_config
        
    except Exception as e:
        logger.error(f"Failed to get subnet config: {str(e)}")
        raise ValueError(f"Failed to retrieve subnet configuration: {str(e)}")


def list_route_tables(credentials: CredentialManager, folder_id: str = None) -> List[Dict[str, Any]]:
    """List all route tables in specified folder"""
    if not folder_id:
        folder_id = credentials.get_folder_id()
        if not folder_id:
            raise ValueError(Config.FOLDER_NOT_CONFIGURED)
    
    try:
        sdk = get_yc_sdk(credentials)
        rt_service = sdk.client(RouteTableServiceStub)
        
        request = ListRouteTablesRequest(folder_id=folder_id)
        response = rt_service.List(request)
        
        route_tables = []
        for rt in response.route_tables:
            rt_info = {
                "id": rt.id,
                "name": rt.name,
                "description": rt.description,
                "folder_id": rt.folder_id,
                "network_id": rt.network_id,
                "static_routes_count": len(rt.static_routes),
                "created_at": str(rt.created_at) if rt.created_at else None,
            }
            route_tables.append(rt_info)
        
        logger.info(f"Retrieved {len(route_tables)} route tables from folder {folder_id}")
        return route_tables
        
    except Exception as e:
        logger.error(f"Failed to list route tables: {str(e)}")
        raise ValueError(f"Failed to retrieve route tables: {str(e)}")


def get_route_table_details(credentials: CredentialManager, route_table_id: str) -> Dict[str, Any]:
    """Get detailed configuration of a specific route table"""
    try:
        sdk = get_yc_sdk(credentials)
        rt_service = sdk.client(RouteTableServiceStub)
        
        request = GetRouteTableRequest(route_table_id=route_table_id)
        rt = rt_service.Get(request)
        
        static_routes = []
        for route in rt.static_routes:
            route_info = {
                "destination_prefix": route.destination_prefix,
            }
            
            if route.next_hop_address:
                route_info["next_hop_address"] = route.next_hop_address
            elif route.gateway_id:
                route_info["gateway_id"] = route.gateway_id
            
            static_routes.append(route_info)
        
        rt_config = {
            "id": rt.id,
            "name": rt.name,
            "description": rt.description,
            "folder_id": rt.folder_id,
            "network_id": rt.network_id,
            "static_routes": static_routes,
            "created_at": str(rt.created_at) if rt.created_at else None,
        }
        
        logger.info(f"Retrieved route table config for {route_table_id}")
        return rt_config
        
    except Exception as e:
        logger.error(f"Failed to get route table config: {str(e)}")
        raise ValueError(f"Failed to retrieve route table configuration: {str(e)}")


def list_addresses(credentials: CredentialManager, folder_id: str = None) -> List[Dict[str, Any]]:
    """List all static IP addresses in specified folder"""
    if not folder_id:
        folder_id = credentials.get_folder_id()
        if not folder_id:
            raise ValueError(Config.FOLDER_NOT_CONFIGURED)
    
    try:
        sdk = get_yc_sdk(credentials)
        address_service = sdk.client(AddressServiceStub)
        
        request = ListAddressesRequest(folder_id=folder_id)
        response = address_service.List(request)
        
        addresses = []
        for addr in response.addresses:
            addr_info = {
                "id": addr.id,
                "name": addr.name,
                "description": addr.description,
                "folder_id": addr.folder_id,
                "external_ipv4_address": addr.external_ipv4_address.address if addr.external_ipv4_address else None,
                "zone_id": addr.external_ipv4_address.zone_id if addr.external_ipv4_address else None,
                "reserved": addr.reserved,
                "used": addr.used,
                "type": str(addr.type),
                "ip_version": str(addr.ip_version),
                "created_at": str(addr.created_at) if addr.created_at else None,
            }
            addresses.append(addr_info)
        
        logger.info(f"Retrieved {len(addresses)} addresses from folder {folder_id}")
        return addresses
        
    except Exception as e:
        logger.error(f"Failed to list addresses: {str(e)}")
        raise ValueError(f"Failed to retrieve addresses: {str(e)}")


def get_address_details(credentials: CredentialManager, address_id: str) -> Dict[str, Any]:
    """Get detailed configuration of a specific static IP address"""
    try:
        sdk = get_yc_sdk(credentials)
        address_service = sdk.client(AddressServiceStub)
        
        request = GetAddressRequest(address_id=address_id)
        addr = address_service.Get(request)
        
        addr_config = {
            "id": addr.id,
            "name": addr.name,
            "description": addr.description,
            "folder_id": addr.folder_id,
            "external_ipv4_address": addr.external_ipv4_address.address if addr.external_ipv4_address else None,
            "zone_id": addr.external_ipv4_address.zone_id if addr.external_ipv4_address else None,
            "reserved": addr.reserved,
            "used": addr.used,
            "type": str(addr.type),
            "ip_version": str(addr.ip_version),
            "created_at": str(addr.created_at) if addr.created_at else None,
        }
        
        logger.info(f"Retrieved address config for {address_id}")
        return addr_config
        
    except Exception as e:
        logger.error(f"Failed to get address config: {str(e)}")
        raise ValueError(f"Failed to retrieve address configuration: {str(e)}")


def list_gateways(credentials: CredentialManager, folder_id: str = None) -> List[Dict[str, Any]]:
    """List all gateways in specified folder"""
    if not folder_id:
        folder_id = credentials.get_folder_id()
        if not folder_id:
            raise ValueError(Config.FOLDER_NOT_CONFIGURED)
    
    try:
        sdk = get_yc_sdk(credentials)
        gateway_service = sdk.client(GatewayServiceStub)
        
        request = ListGatewaysRequest(folder_id=folder_id)
        response = gateway_service.List(request)
        
        gateways = []
        for gw in response.gateways:
            gw_info = {
                "id": gw.id,
                "name": gw.name,
                "description": gw.description,
                "folder_id": gw.folder_id,
                "created_at": str(gw.created_at) if gw.created_at else None,
            }
            
            if gw.shared_egress_gateway:
                gw_info["type"] = "shared_egress_gateway"
            
            gateways.append(gw_info)
        
        logger.info(f"Retrieved {len(gateways)} gateways from folder {folder_id}")
        return gateways
        
    except Exception as e:
        logger.error(f"Failed to list gateways: {str(e)}")
        raise ValueError(f"Failed to retrieve gateways: {str(e)}")


def get_gateway_details(credentials: CredentialManager, gateway_id: str) -> Dict[str, Any]:
    """Get detailed configuration of a specific gateway"""
    try:
        sdk = get_yc_sdk(credentials)
        gateway_service = sdk.client(GatewayServiceStub)
        
        request = GetGatewayRequest(gateway_id=gateway_id)
        gw = gateway_service.Get(request)
        
        gw_config = {
            "id": gw.id,
            "name": gw.name,
            "description": gw.description,
            "folder_id": gw.folder_id,
            "created_at": str(gw.created_at) if gw.created_at else None,
        }
        
        if gw.shared_egress_gateway:
            gw_config["type"] = "shared_egress_gateway"
        
        logger.info(f"Retrieved gateway config for {gateway_id}")
        return gw_config
        
    except Exception as e:
        logger.error(f"Failed to get gateway config: {str(e)}")
        raise ValueError(f"Failed to retrieve gateway configuration: {str(e)}")