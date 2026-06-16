#!/usr/bin/env python3
"""
Test Upload Script for PSGC FHIR CodeSystem

This script uploads the PSGC FHIR CodeSystem to the tx.fhirlab.net server
with a test ID for safe testing purposes.
"""

import json
import requests
import argparse
import os
import sys
import glob
import logging
from typing import Dict, Any, Optional
from copy import deepcopy
from psgc_fhir_converter import validate_fhir_codesystem_structure, validate_against_fhir_terminology_server_requirements


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
    import math
    
    if isinstance(obj, dict):
        return {key: handle_nan_in_data(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [handle_nan_in_data(item) for item in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    else:
        return obj


def modify_codesystem_for_test(fhir_codesystem: Dict[str, Any], test_id: str) -> Dict[str, Any]:
    """
    Modify a FHIR CodeSystem to use a test ID and other test-specific values.
    
    This function replaces the previous approach using json.loads(json.dumps(fhir_codesystem))
    for deep copying, which would fail when the FHIR CodeSystem contained NaN values
    (typically originating from pandas DataFrames). NaN values are not JSON serializable,
    so the json round-trip approach would raise a "not JSON compliant" error.
    
    Args:
        fhir_codesystem (Dict[str, Any]): Original FHIR CodeSystem (may contain NaN values)
        test_id (str): Test ID to use for the CodeSystem
        
    Returns:
        Dict[str, Any]: Modified FHIR CodeSystem with test values
    """
    # Create a deep copy of the original codesystem using copy.deepcopy to avoid JSON serialization issues with NaN
    # Additionally, handle any NaN values by converting them to None to ensure JSON compliance
    fhir_codesystem_safe = handle_nan_in_data(deepcopy(fhir_codesystem))
    
    # Modify the ID to use the test ID
    fhir_codesystem_safe['id'] = test_id
    
    # Modify the URL to use a completely different test URI to avoid conflicts with the original
    if 'url' in fhir_codesystem_safe:
        # Instead of appending -test to the original URL, use a completely different test URI
        # This prevents "multiple-matches" errors when both URIs exist on the server
        original_url = fhir_codesystem_safe['url']
        # Extract the original path part after the domain
        path_parts = original_url.split('/', 3)  # Split into ['https:', '', 'domain', 'path...']
        if len(path_parts) >= 4:
            path_part = path_parts[3]
        else:
            path_part = 'psgc'  # Fallback if original structure is unexpected
        
        # Create a completely different test URI to avoid conflicts
        new_url = f'https://test.upmsilab.org/{path_part}-test'
        fhir_codesystem_safe['url'] = new_url
        
        # Also update the valueSet property if it exists, to match the new URL
        # This prevents "multiple-matches" errors when the FHIR server checks the implicit ValueSet
        if 'valueSet' in fhir_codesystem_safe and fhir_codesystem_safe['valueSet'] == original_url:
            fhir_codesystem_safe['valueSet'] = new_url
    
    # Add a test-specific title
    if 'title' in fhir_codesystem_safe:
        original_title = fhir_codesystem_safe['title']
        fhir_codesystem_safe['title'] = f"[TEST] {original_title}"
    
    # Update status to draft if not already
    fhir_codesystem_safe['status'] = 'draft'
    
    return fhir_codesystem_safe


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


def upload_codesystem_to_server(fhir_codesystem: Dict[str, Any], server_url: str) -> bool:
    """
    Upload the FHIR CodeSystem to the specified server.
    
    This function handles potential NaN (Not a Number) values in the FHIR CodeSystem
    that could cause JSON serialization errors during the upload process.
    It uses PUT to update an existing resource if one with the same ID already exists.
    
    Args:
        fhir_codesystem (Dict[str, Any]): The FHIR CodeSystem to upload (may contain NaN values)
        server_url (str): Base URL of the FHIR server
        
    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        headers = get_auth_headers()
        
        # Use PUT to update the resource with the specific ID, which will overwrite if it exists
        codesystem_id = fhir_codesystem.get('id', 'unknown')
        upload_url = f"{server_url.rstrip('/')}/CodeSystem/{codesystem_id}"
        
        # Handle NaN values before uploading to prevent JSON serialization errors
        # NaN values (from pandas DataFrames) are not JSON serializable
        safe_fhir_codesystem = handle_nan_in_data(fhir_codesystem)
        
        # Make the PUT request to update/create the resource with this ID
        response = requests.put(upload_url, json=safe_fhir_codesystem, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:  # Success or created
            logger.info(f"Successfully uploaded/updated CodeSystem with ID: {codesystem_id}")
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
    parser = argparse.ArgumentParser(description='Upload PSGC FHIR CodeSystem and ValueSets to server with test ID')
    parser.add_argument('--input', required=True, help='Input FHIR CodeSystem JSON file path')
    parser.add_argument('--server-url', required=True, help='FHIR server URL (e.g., https://tx.fhirlab.net/fhir)')
    parser.add_argument('--test-id', default='test-PSGC',
                       help='Test ID to use (default: test-PSGC)')
    parser.add_argument('--valuesets-dir', help='Directory containing ValueSet-*.json files to upload after CodeSystem')
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
    
    logger.info(f"Modifying CodeSystem for test with ID: {args.test_id}")
    test_codesystem = modify_codesystem_for_test(fhir_codesystem, args.test_id)
    
    if not validate_fhir_for_upload(test_codesystem):
        logger.error("Modified CodeSystem failed validation")
        sys.exit(1)
    
    if args.dry_run:
        logger.info("=== DRY RUN ===")
        logger.info(f"Would upload CodeSystem: {test_codesystem['id']}")
        logger.info(f"Server: {args.server_url}")
        if args.valuesets_dir:
            vs_files = sorted(glob.glob(os.path.join(args.valuesets_dir, "ValueSet-*.json")))
            for vf in vs_files:
                logger.info(f"  + {os.path.basename(vf)}")
        return 0
    
    logger.info(f"Uploading test CodeSystem to: {args.server_url}")
    if not upload_codesystem_to_server(test_codesystem, args.server_url):
        logger.error("Test CodeSystem upload failed")
        sys.exit(1)
    
    if args.valuesets_dir:
        logger.info(f"Uploading ValueSets from: {args.valuesets_dir}")
        vs_files = sorted(glob.glob(os.path.join(args.valuesets_dir, "ValueSet-*.json")))
        succeeded = 0
        for vs_path in vs_files:
            resource = load_fhir_codesystem(vs_path)
            if not resource:
                logger.error(f"Failed to load {vs_path}")
                continue
            safe = handle_nan_in_data(deepcopy(resource))
            safe["id"] = f"test-{resource.get('id', 'unknown')}"
            if "url" in safe:
                safe["url"] = safe["url"].replace("fhir.doh.gov.ph", "test.fhir.doh.gov.ph")
            headers = get_auth_headers()
            vs_id = safe["id"]
            resp = requests.put(
                f"{args.server_url.rstrip('/')}/ValueSet/{vs_id}",
                json=safe, headers=headers, timeout=30
            )
            count = len(safe.get("compose", {}).get("include", [{}])[0].get("concept", []))
            if resp.status_code in [200, 201]:
                logger.info(f"  {vs_id} ({count} concepts) OK")
                succeeded += 1
            else:
                logger.error(f"  {vs_id} FAIL ({resp.status_code}): {resp.text[:200]}")
        logger.info(f"ValueSets: {succeeded}/{len(vs_files)} succeeded")
    
    logger.info("Test upload completed")
    return 0


if __name__ == '__main__':
    main()