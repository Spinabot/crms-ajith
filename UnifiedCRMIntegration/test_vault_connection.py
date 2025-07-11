#!/usr/bin/env python3
"""
Test script to debug Vault connection and path structure
"""

import os
import hvac
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_vault_connection():
    """Test Vault connection and explore the structure"""

    # Vault configuration
    vault_url = os.getenv('VAULT_URL', 'http://localhost:8200')
    vault_token = os.getenv('VAULT_TOKEN')
    vault_namespace = os.getenv('VAULT_NAMESPACE')
    secret_path = os.getenv('VAULT_SECRET_PATH', 'crm-integration')

    print("🔍 Vault Connection Test")
    print("=" * 50)
    print(f"URL: {vault_url}")
    print(f"Namespace: {vault_namespace}")
    print(f"Token: {'✅ Set' if vault_token else '❌ Not set'}")
    print(f"Secret Path: {secret_path}")
    print()

    if not vault_token:
        print("❌ VAULT_TOKEN is required")
        return False

    try:
        # Initialize Vault client
        client = hvac.Client(
            url=vault_url,
            token=vault_token,
            namespace=vault_namespace
        )

        # Test authentication
        if not client.is_authenticated():
            print("❌ Authentication failed")
            return False

        print("✅ Authentication successful")

        # Test health
        try:
            health = client.sys.read_health_status()
            print(f"✅ Vault health: {health.get('initialized', False)}")
            print(f"✅ Vault version: {health.get('version', 'Unknown')}")
        except Exception as e:
            print(f"⚠️  Could not get health status: {e}")

        # List available auth methods
        print("\n🔍 Available Auth Methods:")
        try:
            auth_methods = client.sys.list_auth_methods()
            if auth_methods and 'data' in auth_methods:
                for method in auth_methods['data'].keys():
                    print(f"   - {method}")
        except Exception as e:
            print(f"   Error: {e}")

        # List available secret engines
        print("\n🔍 Available Secret Engines:")
        try:
            mounts = client.sys.list_mounted_secrets_engines()
            if mounts and 'data' in mounts:
                for mount_path, mount_info in mounts['data'].items():
                    print(f"   - {mount_path}: {mount_info.get('type', 'unknown')}")
                    print(f"     Options: {mount_info.get('options', {})}")
        except Exception as e:
            print(f"   Error: {e}")

        # Try different mount points and paths
        print("\n🔍 Testing Different Paths:")

        # Test 1: Standard secret mount
        test_paths = [
            ('secret', 'crm-integration'),
            ('secret', secret_path),
            ('Secrets/kv', 'spinabot/dev/app-secrets/CRM-Integration'),
            ('Secrets/kv/spinabot/dev/app-secrets', 'CRM-Integration'),
            ('Secrets', 'kv/spinabot/dev/app-secrets/CRM-Integration'),
        ]

        for mount_point, path in test_paths:
            print(f"\n   Testing: mount_point='{mount_point}', path='{path}'")
            try:
                response = client.secrets.kv.v2.read_secret_version(
                    path=path,
                    mount_point=mount_point
                )
                if response and 'data' in response and 'data' in response['data']:
                    print(f"   ✅ SUCCESS! Found {len(response['data']['data'])} secrets")
                    for key in response['data']['data'].keys():
                        print(f"      - {key}")
                    return True
                else:
                    print(f"   ⚠️  Response format unexpected: {response}")
            except Exception as e:
                print(f"   ❌ Failed: {e}")

        # If we get here, try listing secrets at different paths
        print("\n🔍 Trying to list secrets at different paths:")
        list_paths = [
            ('secret', ''),
            ('Secrets/kv', ''),
            ('Secrets/kv/spinabot', ''),
            ('Secrets/kv/spinabot/dev', ''),
            ('Secrets/kv/spinabot/dev/app-secrets', ''),
        ]

        for mount_point, path in list_paths:
            print(f"\n   Listing: mount_point='{mount_point}', path='{path}'")
            try:
                response = client.secrets.kv.v2.list_secrets(
                    path=path,
                    mount_point=mount_point
                )
                if response and 'data' in response and 'keys' in response['data']:
                    print(f"   ✅ Found keys: {response['data']['keys']}")
                else:
                    print(f"   ⚠️  No keys found or unexpected response")
            except Exception as e:
                print(f"   ❌ Failed: {e}")

        return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_vault_connection()