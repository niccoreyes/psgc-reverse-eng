#!/usr/bin/env python3
"""
Production Upload Script for PSGC FHIR CodeSystem

This script uploads the PSGC FHIR CodeSystem to the tx.fhirlab.net server
with the original ID for production use.
"""

import json
import requests
import argparse
import os
import sys
import logging
from typing import Dict, Any, Optional
import time
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


def load_fhir_codesystem(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load FHIR CodeSystem from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file containing the FHIR CodeSystem
        
    Returns:
        Optional[Dict[str, Any]]: The loaded FHIR CodeSystem or None if failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error loading FHIR CodeSystem from {file_path}: {str(e)}")
        return None


def validate_fhir_for_upload(fhir_codesystem: Dict[str, Any]) -> bool:
    """
    Validate the FHIR CodeSystem before uploading.
    
    Args:
        fhir_codesystem (Dict[str, Any]): The FHIR CodeSystem to validate
        
    Returns:
        bool: True if valid for upload, False otherwise
    """
    logger.info("Validating FHIR CodeSystem structure...")
    
    # Basic FHIR CodeSystem validation
    basic_valid = validate_fhir_codesystem_structure(fhir_codesystem)
    if not basic_valid:
        logger.error("FHIR CodeSystem basic structure validation failed")
        return False
    
    # Terminology server requirements validation
    term_valid = validate_against_fhir_terminology_server_requirements(fhir_codesystem)
    if not term_valid:
        logger.error("FHIR CodeSystem terminology server validation failed")
        return False
    
    logger.info("FHIR CodeSystem validation passed")
    return True


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


def get_existing_codesystem(server_url: str, codesystem_id: str) -> Optional[Dict[str, Any]]:
    """
    Check if a CodeSystem with the given ID already exists on the server.
    
    Args:
        server_url (str): Base URL of the FHIR server
        codesystem_id (str): ID of the CodeSystem to check
        
    Returns:
        Optional[Dict[str, Any]]: Existing CodeSystem if found, None otherwise
    """
    try:
        headers = get_auth_headers()
        
        # Construct the URL for the specific CodeSystem
        codesystem_url = f"{server_url.rstrip('/')}/CodeSystem/{codesystem_id}"
        
        response = requests.get(codesystem_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            logger.warning(f"Error checking for existing CodeSystem: {response.status_code}")
            logger.warning(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"Request error while checking existing CodeSystem: {str(e)}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error while checking existing CodeSystem: {str(e)}")
        return None


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


def upload_codesystem_to_server(fhir_codesystem: Dict[str, Any], server_url: str) -> bool:
    """
    Upload the FHIR CodeSystem to the specified server.
    
    This function handles potential NaN (Not a Number) values in the FHIR CodeSystem
    that could cause JSON serialization errors during the upload process.
    
    Args:
        fhir_codesystem (Dict[str, Any]): The FHIR CodeSystem to upload (may contain NaN values)
        server_url (str): Base URL of the FHIR server
        
    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        headers = get_auth_headers()
        
        # Check if the CodeSystem already exists
        existing_codesystem = get_existing_codesystem(server_url, fhir_codesystem.get('id', ''))
        
        # Construct the full URL for the upload
        if existing_codesystem:
            # PUT to update existing resource
            upload_url = f"{server_url.rstrip('/')}/CodeSystem/{fhir_codesystem['id']}"
            method = requests.put
            logger.info(f"Updating existing CodeSystem with ID: {fhir_codesystem['id']}")
        else:
            # POST to create new resource
            upload_url = f"{server_url.rstrip('/')}/CodeSystem"
            method = requests.post
            logger.info(f"Creating new CodeSystem with ID: {fhir_codesystem['id']}")
        
        # Handle NaN values before uploading to prevent JSON serialization errors
        # NaN values (from pandas DataFrames) are not JSON serializable
        safe_fhir_codesystem = handle_nan_in_data(fhir_codesystem)
        
        # Make the request to create/update the resource
        response = method(upload_url, json=safe_fhir_codesystem, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:  # Success or created
            logger.info(f"Successfully uploaded CodeSystem with ID: {fhir_codesystem.get('id', 'unknown')}")
            logger.info(f"Response: {response.status_code}")
            return True
        else:
            logger.error(f"Upload failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during upload: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        return False


def main():
    """Main function to run the production upload script."""
    parser = argparse.ArgumentParser(description='Upload PSGC FHIR CodeSystem to server with original ID for production')
    parser.add_argument('--input', required=True, help='Input FHIR JSON file path')
    parser.add_argument('--server-url', required=True, help='FHIR server URL (e.g., https://tx.fhirlab.net/fhir)')
    parser.add_argument('--confirm', action='store_true', 
                       help='Confirm without prompting (use with caution in production)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Perform a dry run without actually uploading')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Load the FHIR CodeSystem from file
    fhir_codesystem = load_fhir_codesystem(args.input)
    if not fhir_codesystem:
        logger.error("Failed to load FHIR CodeSystem from file")
        sys.exit(1)
    
    # Validate the CodeSystem
    if not validate_fhir_for_upload(fhir_codesystem):
        logger.error("CodeSystem failed validation")
        sys.exit(1)
    
    # Production safety check
    original_id = fhir_codesystem.get('id', 'unknown')
    logger.info(f"Preparing to upload CodeSystem with ID: {original_id}")
    
    if not args.confirm and not args.dry_run:
        if not prompt_user_confirmation(f"Are you sure you want to upload the CodeSystem with ID '{original_id}' to production? This cannot be undone."):
            logger.info("Upload cancelled by user")
            return 0
    
    if args.dry_run:
        logger.info("Dry run mode: Skipping actual upload")
        logger.info(f"Would upload CodeSystem with ID: {original_id}")
        logger.info(f"Server URL: {args.server_url}")
        return 0
    else:
        # Upload the CodeSystem to the server
        logger.info(f"Uploading production CodeSystem to: {args.server_url}")
        success = upload_codesystem_to_server(fhir_codesystem, args.server_url)
        
        if success:
            logger.info("Production upload completed successfully")
            return 0
        else:
            logger.error("Production upload failed")
            sys.exit(1)


if __name__ == '__main__':
    main()