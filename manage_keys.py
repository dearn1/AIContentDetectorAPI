"""
API Key Management Script

This script helps manage API keys stored in environment variables.
Keys are stored in the API_KEYS environment variable as a JSON array.
"""
import argparse
import os
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv
from app.security.api_auth import (
    API_KEYS, 
    create_api_key, 
    get_api_key,
    API_KEYS_ENV,
    DEFAULT_RATE_LIMIT
)

# Load environment variables from .env file
load_dotenv()

def save_api_keys_to_env():
    """Save API keys to environment variable and .env file"""
    keys_data = []
    for key_data in API_KEYS.values():
        key_dict = {
            'key': key_data.key,
            'name': key_data.name,
            'is_active': key_data.is_active,
            'rate_limit': key_data.rate_limit,
            'created_at': key_data.created_at.isoformat(),
        }
        if key_data.expires_at:
            key_dict['expires_at'] = key_data.expires_at.isoformat()
        keys_data.append(key_dict)
    
    # Update environment variable
    os.environ[API_KEYS_ENV] = json.dumps(keys_data)
    
    # Update .env file
    env_file = ".env"
    env_lines = []
    
    # Read existing .env file if it exists
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    # Update or add API_KEYS line
    api_keys_line = f"{API_KEYS_ENV}='{json.dumps(keys_data, indent=2)}'\n"
    found = False
    for i, line in enumerate(env_lines):
        if line.startswith(f"{API_KEYS_ENV}="):
            env_lines[i] = api_keys_line
            found = True
            break
    
    if not found:
        env_lines.append(api_keys_line)
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(env_lines)

def list_keys(show_keys: bool = False) -> None:
    """List all API keys"""
    if not API_KEYS:
        print("No API keys found.")
        return
    
    print("\nAPI Keys:")
    print("-" * 80)
    for i, (key, key_data) in enumerate(API_KEYS.items(), 1):
        print(f"{i}. Name: {key_data.name}")
        if show_keys:
            print(f"   Key: {key}")
        else:
            print(f"   Key: {'*' * 8}{key[-4:]}")
        print(f"   Status: {'Active' if key_data.is_valid else 'Inactive'}")
        print(f"   Rate Limit: {key_data.rate_limit} requests/day")
        print(f"   Created: {key_data.created_at.strftime('%Y-%m-%d')}")
        if key_data.expires_at:
            days_left = (key_data.expires_at - datetime.utcnow()).days
            print(f"   Expires: {key_data.expires_at.strftime('%Y-%m-%d')} ({days_left} days remaining)")
        print("-" * 80)

def create_key(name: str, rate_limit: int, days_valid: int) -> None:
    """Create a new API key"""
    if not name:
        print("Error: Name is required")
        return
    
    key_data = create_api_key(
        name=name,
        rate_limit=rate_limit,
        days_valid=days_valid
    )
    
    # Save to .env file
    save_api_keys_to_env()
    
    print("\n✅ API Key created successfully!")
    print("-" * 80)
    print(f"Name: {key_data.name}")
    print(f"Key: {key_data.key}")
    print(f"Rate Limit: {key_data.rate_limit} requests/day")
    if key_data.expires_at:
        print(f"Expires: {key_data.expires_at.strftime('%Y-%m-%d')}")
    print("\nIMPORTANT: Save this key securely. It won't be shown again!")
    print("-" * 80)
    print("\nTo use this key, add it to your .env file or set it as an environment variable:")
    print(f"export {API_KEYS_ENV}='{json.dumps([{"name": key_data.name, "key": key_data.key, "rate_limit": key_data.rate_limit}], indent=2)}'")
    print("-" * 80)

def revoke_key(key: str) -> None:
    """Revoke an API key"""
    key_data = get_api_key(key)
    if not key_data:
        print(f"Error: API key not found")
        return
    
    key_data.is_active = False
    save_api_keys_to_env()
    print(f"✅ API key '{key_data.name}' has been revoked and saved to .env file.")
    print("Restart your application for changes to take effect.")

def main():
    parser = argparse.ArgumentParser(description="Manage API keys")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all API keys")
    list_parser.add_argument("--show-keys", action="store_true", help="Show full API keys (use with caution)")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new API key")
    create_parser.add_argument("--name", required=True, help="Name for the API key")
    create_parser.add_argument("--rate-limit", type=int, default=1000, 
                             help="Daily rate limit (default: 1000)")
    create_parser.add_argument("--days-valid", type=int, default=365,
                             help="Number of days the key is valid (default: 365)")
    
    # Revoke command
    revoke_parser = subparsers.add_parser("revoke", help="Revoke an API key")
    revoke_parser.add_argument("key", help="The API key to revoke")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "list":
        list_keys(show_keys=args.show_keys)
    elif args.command == "create":
        create_key(args.name, args.rate_limit, args.days_valid)
    elif args.command == "revoke":
        revoke_key(args.key)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
