#!/usr/bin/env python3
"""
Test script for Yandex Cloud MCP Server
"""

import os
from src.yandex_cloud_mcp.credentials import CredentialManager
from src.yandex_cloud_mcp.compute import list_vms, get_vm_config
from src.yandex_cloud_mcp.network import list_networks, list_subnets, list_security_groups
from src.yandex_cloud_mcp.storage import list_disks, list_snapshots

def test_functions():
    """Test MCP server functions"""
    
    print("=== Testing Modular Yandex Cloud MCP Server ===\n")
    
    # Create credential manager and use environment variables
    credentials = CredentialManager()
    
    # Test VMs
    print("1. Testing VMs...")
    try:
        vms = list_vms(credentials)
        print(f"Found {len(vms)} VMs:")
        for vm in vms[:3]:  # Show first 3
            print(f"  - {vm['name']} ({vm['id']}) - {vm['status']}")
            
        if vms:
            print(f"\nTesting get_vm_config for VM: {vms[0]['id']}")
            config = get_vm_config(credentials, vms[0]['id'])
            print(f"VM Resources: {config.get('resources', {})}")
            
    except Exception as e:
        print(f"VMs Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test Networks
    print("2. Testing Networks...")
    try:
        networks = list_networks(credentials)
        print(f"Found {len(networks)} networks:")
        for net in networks[:3]:  # Show first 3
            print(f"  - {net['name']} ({net['id']})")
    except Exception as e:
        print(f"Networks Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test Subnets
    print("3. Testing Subnets...")
    try:
        subnets = list_subnets(credentials)
        print(f"Found {len(subnets)} subnets:")
        for subnet in subnets[:3]:  # Show first 3
            print(f"  - {subnet['name']} ({subnet['id']}) - {subnet['zone_id']}")
    except Exception as e:
        print(f"Subnets Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test Security Groups
    print("4. Testing Security Groups...")
    try:
        sgs = list_security_groups(credentials)
        print(f"Found {len(sgs)} security groups:")
        for sg in sgs[:3]:  # Show first 3
            print(f"  - {sg['name']} ({sg['id']}) - {sg['rules_count']} rules")
    except Exception as e:
        print(f"Security Groups Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test Disks
    print("5. Testing Disks...")
    try:
        disks = list_disks(credentials)
        print(f"Found {len(disks)} disks:")
        for disk in disks[:3]:  # Show first 3
            print(f"  - {disk['name']} ({disk['id']}) - {disk['size']} bytes")
    except Exception as e:
        print(f"Disks Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test Snapshots
    print("6. Testing Snapshots...")
    try:
        snapshots = list_snapshots(credentials)
        print(f"Found {len(snapshots)} snapshots:")
        for snap in snapshots[:3]:  # Show first 3
            print(f"  - {snap['name']} ({snap['id']}) - {snap['storage_size']} bytes")
    except Exception as e:
        print(f"Snapshots Error: {e}")
    
    print("\n" + "="*50)
    print("✅ Modular test completed!")

if __name__ == "__main__":
    test_functions()