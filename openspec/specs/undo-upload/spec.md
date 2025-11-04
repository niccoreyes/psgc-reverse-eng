# undo-upload Specification

## Purpose
TBD - created by archiving change upload-fhir-resources-to-server. Update Purpose after archive.
## Requirements
### Requirement: Undo Upload Script Creation
A Python script named `undo_fhir_upload.py` SHALL be created to remove or rollback FHIR resources from the tx.fhirlab.net server.

#### Scenario:
- Given an uploaded FHIR resource with a specific ID
- When the user runs `python undo_fhir_upload.py --id <resource_id>`
- Then the script should attempt to delete the resource with the specified ID from the server
- And the script should return a success message upon successful deletion
- And the script should return an appropriate error message if deletion fails

### Requirement: Authentication Handling
The undo script SHALL securely handle authentication to the tx.fhirlab.net server.

#### Scenario:
- Given the environment variables FHIR_SERVER_API_KEY and FHIR_SERVER_URL are set
- When the undo script attempts to connect to the server
- Then it should use the API key from the environment variable for authentication
- And it should not hardcode credentials in the script

### Requirement: Resource Lookup Before Deletion
Before attempting to delete a resource, the script SHALL verify that the resource exists on the server.

#### Scenario:
- Given a resource ID for deletion
- When the undo script runs the lookup process
- Then it should first query the server for the resource with the specified ID
- And it should confirm the resource exists before attempting deletion
- And it should return an error if the resource is not found

### Requirement: Confirmation Prompt
The undo script SHALL prompt the user for confirmation before deleting a resource to prevent accidental deletions.

#### Scenario:
- Given a resource ID to delete
- When the undo script is executed
- Then it should display information about the resource to be deleted
- And it should ask for user confirmation before proceeding
- And it should only proceed with deletion if the user confirms

### Requirement: Error Handling
The script SHALL provide comprehensive error handling for various failure scenarios.

#### Scenario:
- Given an undo operation
- When network errors occur
- Then the script should catch the exception and return a meaningful error message
- When authentication fails
- Then the script should return an authentication error
- When server returns an error status code
- Then the script should return the server response with appropriate error message
- When the resource doesn't exist on the server
- Then the script should return a resource not found error

### Requirement: Alternative: Version Rollback
If the server supports versioning, the undo script SHALL be able to rollback to a previous version instead of deleting entirely.

#### Scenario:
- Given a versioned FHIR resource on the server
- When the undo script is executed with a version parameter
- Then it should attempt to revert to the specified previous version
- And it should return success upon successful rollback
- And it should fall back to deletion if version rollback is not possible

