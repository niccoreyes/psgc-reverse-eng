#!/usr/bin/env python3
"""
Undo Script for PSGC FHIR CodeSystem

This script deletes or rolls back uploaded PSGC FHIR CodeSystem resources 
from the tx.fhirlab.net server in case of issues.
"""

import json
import requests
import argparse
import os
import sys
import logging
from typing import Dict, Any, Optional
import math
from psgc_fhir_converter import validate_fhir_codesystem_structure, validate_against_fhir_terminology_server_requirements


def handle_nan_in_data(obj):
    """
    Recursively handle NaN values in data structures, converting them to None.
    
    This function is critical for handling data that originates from pandas DataFrames,
    which use NaN (Not a Number) to represent missing numeric values. Since NaN is not
    valid JSON, attempting to serialize data containing NaN values will result in a
    "Out of range float values are not JSON compliant: nan" error.
    
    Args:
        obj: The data structure to process (dict, list, or primitive)
        
    Returns:
        Processed data structure with NaN values replaced by None
    """
    if isinstance(obj, dict):
        return {key: handle_nan_in_data(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [handle_nan_in_data(item) for item in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    else:
        return obj


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_auth_headers() -> Dict[str, str]:
    """
    Get authentication headers for the FHIR server.
    
    Returns:
        Dict[str, str]: Authentication headers
    """
    api_key = os.getenv('FHIR_SERVER_API_KEY')
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Add authorization header only if API key is provided
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    return headers


def lookup_codesystem(server_url: str, codesystem_id: str) -> Optional[Dict[str, Any]]:
    """
    Lookup a CodeSystem by ID on the server.
    
    Args:
        server_url (str): Base URL of the FHIR server
        codesystem_id (str): ID of the CodeSystem to lookup
        
    Returns:
        Optional[Dict[str, Any]]: CodeSystem if found, None otherwise
    """
    try:
        headers = get_auth_headers()
        
        # Construct the URL for the specific CodeSystem
        codesystem_url = f"{server_url.rstrip('/')}/CodeSystem/{codesystem_id}"
        
        response = requests.get(codesystem_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.info(f"CodeSystem with ID '{codesystem_id}' not found on server")
            return None
        else:
            logger.error(f"Error looking up CodeSystem: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during lookup: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during lookup: {str(e)}")
        return None


def delete_codesystem(server_url: str, codesystem_id: str) -> bool:
    """
    Delete a CodeSystem by ID from the server.
    
    Args:
        server_url (str): Base URL of the FHIR server
        codesystem_id (str): ID of the CodeSystem to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        headers = get_auth_headers()
        
        # Construct the URL for the specific CodeSystem
        codesystem_url = f"{server_url.rstrip('/')}/CodeSystem/{codesystem_id}"
        
        response = requests.delete(codesystem_url, headers=headers, timeout=30)
        
        if response.status_code == 200 or response.status_code == 204:
            logger.info(f"Successfully deleted CodeSystem with ID: {codesystem_id}")
            return True
        else:
            logger.error(f"Failed to delete CodeSystem: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during deletion: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during deletion: {str(e)}")
        return False


def prompt_user_confirmation(message: str) -> bool:
    """
    Prompt the user for confirmation before proceeding.
    
    Args:
        message (str): Message to display to the user
        
    Returns:
        bool: True if user confirms, False otherwise
    """
    response = input(f"{message} (yes/no): ").strip().lower()
    return response in ['yes', 'y']


def main():
    """Main function to run the undo script."""
    parser = argparse.ArgumentParser(description='Delete or rollback uploaded PSGC FHIR CodeSystem from server')
    parser.add_argument('--server-url', required=True, help='FHIR server URL (e.g., https://tx.fhirlab.net/fhir)')
    parser.add_argument('--codesystem-id', required=True, help='ID of the CodeSystem to delete')
    parser.add_argument('--confirm', action='store_true', 
                       help='Confirm without prompting (use with caution)')
    parser.add_argument('--no-prompt', action='store_true', 
                       help='Skip confirmation prompt (same as --confirm)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Lookup the CodeSystem on the server
    logger.info(f"Looking up CodeSystem with ID: {args.codesystem_id}")
    existing_codesystem = lookup_codesystem(args.server_url, args.codesystem_id)
    
    if not existing_codesystem:
        logger.info(f"No CodeSystem found with ID: {args.codesystem_id}")
        return 0
    
    logger.info(f"Found CodeSystem: {existing_codesystem.get('title', 'Unknown')} (Version: {existing_codesystem.get('version', 'Unknown')})")
    
    # Confirm deletion
    should_proceed = args.confirm or args.no_prompt
    if not should_proceed:
        should_proceed = prompt_user_confirmation(f"Are you sure you want to delete the CodeSystem with ID '{args.codesystem_id}'? This cannot be undone.")
    
    if not should_proceed:
        logger.info("Deletion cancelled by user")
        return 0
    
    # Delete the CodeSystem from the server
    logger.info(f"Deleting CodeSystem with ID: {args.codesystem_id}")
    success = delete_codesystem(args.server_url, args.codesystem_id)
    
    if success:
        logger.info("Undo operation completed successfully")
        return 0
    else:
        logger.error("Undo operation failed")
        sys.exit(1)


if __name__ == '__main__':
    main()