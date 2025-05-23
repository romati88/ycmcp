#!/usr/bin/env python3
"""
Test script for Yandex Cloud MCP Server
"""

import os
from src.yandex_cloud_mcp.credentials import CredentialManager
from src.yandex_cloud_mcp.compute import (
    list_vms, get_vm_config, list_images, list_zones, list_disk_types
)
from src.yandex_cloud_mcp.network import (
    list_networks, list_subnets, list_security_groups, 
    list_route_tables, list_addresses, list_gateways
)
from src.yandex_cloud_mcp.storage import list_disks, list_snapshots
from src.yandex_cloud_mcp.resource_manager import (
    list_clouds, list_folders, get_organization_context, suggest_scope_for_query
)

def test_functions():
    """Test MCP server functions"""
    
    print("=== Testing Enhanced Yandex Cloud MCP Server ===\n")
    
    # Create credential manager and use environment variables
    credentials = CredentialManager()
    
    # Test credentials status
    print("0. Testing Credentials...")
    token = credentials.get_token()
    folder_id = credentials.get_folder_id()
    print(f"IAM Token: {'✅ Available' if token else '❌ Not configured'}")
    print(f"Folder ID: {'✅ Available' if folder_id else '❌ Not configured'}")
    
    if not token or not folder_id:
        print("\n⚠️  Please set YC_TOKEN and YC_FOLDER_ID environment variables or configure credentials.")
        print("   Use: export YC_TOKEN=$(yc iam create-token)")
        print("   Use: export YC_FOLDER_ID=$(yc config get folder-id)")
        return
    
    print("\n" + "="*50 + "\n")
    
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
    
    print("\n" + "="*50 + "\n")
    
    # Test Cloud/Organization level operations
    print("7. Testing Cloud/Organization Level...")
    try:
        clouds = list_clouds(credentials)
        print(f"Found {len(clouds)} clouds:")
        for cloud in clouds[:3]:  # Show first 3
            print(f"  - {cloud['name']} ({cloud['id']}) - Org: {cloud.get('organization_id', 'N/A')}")
    except Exception as e:
        print(f"Clouds Error: {e}")
    
    print("\n" + "-"*30 + "\n")
    
    # Test smart folder listing (auto-detects cloud_id)
    try:
        folders = list_folders(credentials)
        if folders and folders[0].get("error") == "cloud_id_required":
            print("Smart folder listing - showing available clouds:")
            for cloud in folders[0]["available_clouds"]:
                print(f"  📁 Cloud: {cloud['name']} ({cloud['id']})")
            print(f"💡 Suggestion: {folders[0]['suggestion']}")
        else:
            print(f"Found {len(folders)} folders (auto-selected single cloud):")
            for folder in folders[:3]:  # Show first 3
                print(f"  - {folder['name']} ({folder['id']}) - Cloud: {folder['cloud_id']}")
    except Exception as e:
        print(f"Folders Error: {e}")
    
    print("\n" + "-"*30 + "\n")
    
    # Test organization context
    try:
        context = get_organization_context(credentials)
        print(f"📊 Organization Context:")
        print(f"  • Clouds: {len(context['clouds'])}")
        print(f"  • Total Folders: {context['total_folders']}")
        print(f"  • Organization ID: {context['organization_id']}")
    except Exception as e:
        print(f"Organization Context Error: {e}")
    
    print("\n" + "-"*30 + "\n")
    
    # Test scope suggestions
    try:
        print("🎯 Scope Suggestions for different resources:")
        for resource in ["vms", "networks", "zones"]:
            suggestions = suggest_scope_for_query(credentials, resource)
            print(f"  {resource}: {suggestions['recommendations'][0] if suggestions['recommendations'] else 'No specific recommendation'}")
    except Exception as e:
        print(f"Scope Suggestions Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test Extended Compute operations
    print("8. Testing Extended Compute...")
    try:
        images = list_images(credentials)
        print(f"Found {len(images)} images:")
        for image in images[:3]:  # Show first 3
            print(f"  - {image['name']} ({image['id']}) - Family: {image.get('family', 'N/A')}")
    except Exception as e:
        print(f"Images Error: {e}")
    
    print("\n" + "-"*30 + "\n")
    
    try:
        zones = list_zones(credentials)
        print(f"Found {len(zones)} zones:")
        for zone in zones[:5]:  # Show first 5
            print(f"  - {zone['id']} - Region: {zone['region_id']} - Status: {zone['status']}")
    except Exception as e:
        print(f"Zones Error: {e}")
    
    print("\n" + "-"*30 + "\n")
    
    try:
        disk_types = list_disk_types(credentials)
        print(f"Found {len(disk_types)} disk types:")
        for dt in disk_types[:3]:  # Show first 3
            print(f"  - {dt['id']} - Zones: {', '.join(dt['zone_ids'])}")
    except Exception as e:
        print(f"Disk Types Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test Extended VPC operations
    print("9. Testing Extended VPC...")
    try:
        route_tables = list_route_tables(credentials)
        print(f"Found {len(route_tables)} route tables:")
        for rt in route_tables[:3]:  # Show first 3
            print(f"  - {rt['name']} ({rt['id']}) - Routes: {rt['static_routes_count']}")
    except Exception as e:
        print(f"Route Tables Error: {e}")
    
    print("\n" + "-"*30 + "\n")
    
    try:
        addresses = list_addresses(credentials)
        print(f"Found {len(addresses)} static IP addresses:")
        for addr in addresses[:3]:  # Show first 3
            ip = addr.get('external_ipv4_address', 'N/A')
            print(f"  - {addr['name']} ({addr['id']}) - IP: {ip} - Used: {addr['used']}")
    except Exception as e:
        print(f"Addresses Error: {e}")
    
    print("\n" + "-"*30 + "\n")
    
    try:
        gateways = list_gateways(credentials)
        print(f"Found {len(gateways)} gateways:")
        for gw in gateways[:3]:  # Show first 3
            print(f"  - {gw['name']} ({gw['id']}) - Type: {gw.get('type', 'standard')}")
    except Exception as e:
        print(f"Gateways Error: {e}")
    
    print("\n" + "="*50)
    print("✅ Enhanced MCP server test completed!")
    print("\n📊 Summary:")
    print("   ✓ Cloud/Organization level operations")
    print("   ✓ Extended Compute services (VMs, Images, Zones, Disk Types)")
    print("   ✓ Extended VPC services (Networks, Subnets, Route Tables, Addresses, Gateways)")
    print("   ✓ Storage services (Disks, Snapshots)")
    print("   ✓ Security Groups with detailed configurations")

if __name__ == "__main__":
    test_functions()