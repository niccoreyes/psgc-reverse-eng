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
import glob
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
        
        upload_url = f"{server_url.rstrip('/')}/CodeSystem/{fhir_codesystem['id']}"
        method = requests.put
        logger.info(f"Uploading CodeSystem with ID: {fhir_codesystem['id']}")
        
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


def upload_resource_to_server(resource: Dict[str, Any], server_url: str) -> bool:
    resource_type = resource.get("resourceType", "Unknown")
    resource_id = resource.get("id", "unknown")
    try:
        headers = get_auth_headers()
        upload_url = f"{server_url.rstrip('/')}/{resource_type}/{resource_id}"
        safe = handle_nan_in_data(resource)
        response = requests.put(upload_url, json=safe, headers=headers, timeout=30)
        if response.status_code in [200, 201]:
            logger.info(f"  {resource_type}/{resource_id} OK ({response.status_code})")
            return True
        else:
            logger.error(f"  {resource_type}/{resource_id} FAIL ({response.status_code}): {response.text[:200]}")
            return False
    except Exception as e:
        logger.error(f"  {resource_type}/{resource_id} ERROR: {e}")
        return False


def upload_valuesets(valuesets_dir: str, server_url: str, dry_run: bool) -> tuple:
    succeeded = 0
    failed = 0
    vs_files = sorted(glob.glob(os.path.join(valuesets_dir, "ValueSet-*.json")))
    if not vs_files:
        logger.warning(f"No ValueSet-*.json files found in {valuesets_dir}")
        return 0, 0

    for vs_path in vs_files:
        resource = load_fhir_codesystem(vs_path)
        if not resource:
            logger.error(f"Failed to load {vs_path}")
            failed += 1
            continue
        vs_id = resource.get("id", os.path.basename(vs_path))
        count = len(resource.get("compose", {}).get("include", [{}])[0].get("concept", []))
        logger.info(f"ValueSet {vs_id}: {count} concepts")

        if dry_run:
            logger.info(f"  Would upload {vs_id}")
            succeeded += 1
        else:
            if upload_resource_to_server(resource, server_url):
                succeeded += 1
            else:
                failed += 1

    return succeeded, failed


def main():
    parser = argparse.ArgumentParser(description='Upload PSGC FHIR CodeSystem and ValueSets to server')
    parser.add_argument('--input', required=True, help='Input FHIR CodeSystem JSON file path')
    parser.add_argument('--server-url', required=True, help='FHIR server URL (e.g., https://tx.fhirlab.net/fhir)')
    parser.add_argument('--valuesets-dir', help='Directory containing ValueSet-*.json files to upload after CodeSystem')
    parser.add_argument('--confirm', action='store_true',
                       help='Confirm without prompting (use with caution in production)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Perform a dry run without actually uploading')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    fhir_codesystem = load_fhir_codesystem(args.input)
    if not fhir_codesystem:
        logger.error("Failed to load FHIR CodeSystem from file")
        sys.exit(1)
    
    if not validate_fhir_for_upload(fhir_codesystem):
        logger.error("CodeSystem failed validation")
        sys.exit(1)
    
    original_id = fhir_codesystem.get('id', 'unknown')
    vs_count = len(glob.glob(os.path.join(args.valuesets_dir or "", "ValueSet-*.json"))) if args.valuesets_dir else 0
    logger.info(f"Preparing: CodeSystem {original_id}" + (f" + {vs_count} ValueSets" if vs_count else ""))
    
    if not args.confirm and not args.dry_run:
        msg = f"Upload CodeSystem '{original_id}'"
        if vs_count:
            msg += f" and {vs_count} ValueSets"
        msg += " to production? This cannot be undone."
        if not prompt_user_confirmation(msg):
            logger.info("Upload cancelled by user")
            return 0
    
    if args.dry_run:
        logger.info("=== DRY RUN ===")
        logger.info(f"Would upload CodeSystem: {original_id}")
        logger.info(f"Server: {args.server_url}")
        if args.valuesets_dir:
            vs_files = sorted(glob.glob(os.path.join(args.valuesets_dir, "ValueSet-*.json")))
            for vf in vs_files:
                logger.info(f"  + {os.path.basename(vf)}")
        return 0
    
    logger.info(f"Uploading CodeSystem to: {args.server_url}")
    if not upload_codesystem_to_server(fhir_codesystem, args.server_url):
        logger.error("CodeSystem upload failed — stopping before ValueSets")
        sys.exit(1)
    
    if args.valuesets_dir:
        logger.info(f"Uploading ValueSets from: {args.valuesets_dir}")
        succeeded, failed = upload_valuesets(args.valuesets_dir, args.server_url, dry_run=False)
        logger.info(f"ValueSets: {succeeded} succeeded, {failed} failed")
        if failed:
            sys.exit(1)
    
    logger.info("Upload completed successfully")
    return 0


if __name__ == '__main__':
    main()