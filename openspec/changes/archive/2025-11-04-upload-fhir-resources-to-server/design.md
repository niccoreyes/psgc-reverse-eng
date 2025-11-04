## Context
The PSGC to FHIR converter generates JSON CodeSystem resources that need to be deployed to a FHIR terminology server (tx.fhirlab.net) for use in healthcare applications. Currently, there's no automated way to upload these resources to the server, which makes testing and deployment manual and error-prone.

The design needs to address how to interact with the FHIR server API, handle authentication, manage different deployment scenarios (test vs production), and provide safe rollback mechanisms.

## Goals / Non-Goals
- Goals:
  - Develop a reliable way to upload FHIR CodeSystem resources to tx.fhirlab.net
  - Implement test and production deployment options
  - Provide a mechanism to undo uploads if needed
  - Implement proper error handling and validation
  - Ensure authentication and security best practices
- Non-Goals:
  - Modify the existing FHIR conversion logic
  - Change the format or structure of the generated FHIR resources
  - Handle other FHIR resource types beyond CodeSystem
  - Implement complex deployment orchestration

## Decisions
- Decision: Use Python requests library for HTTP communication with the FHIR server
- Decision: Implement separate scripts for test and production deployments to prevent accidental production changes
- Decision: Use environment variables for storing API credentials to avoid hardcoding sensitive information
- Decision: Implement validation checks before upload to prevent sending malformed FHIR resources
- Decision: Implement a dry-run option to preview what would be uploaded without actually doing it

## Risks / Trade-offs
- Data integrity risk → Validate FHIR resource structure before upload
- Security risk → Store credentials in environment variables, not in code
- Production deployment risk → Separate test and production scripts with different IDs
- Revert capability → Implement undo functionality to rollback erroneous changes

## Migration Plan
- Steps: 
  1. Develop and test upload functionality with local FHIR server
  2. Implement test upload script with test ID
  3. Implement production upload script with original ID
  4. Implement undo script
  5. Test all scripts with tx.fhirlab.net server
  6. Update documentation

## Open Questions
- What is the exact API endpoint format for uploading resources to tx.fhirlab.net?
- What authentication method does the server use (API key, OAuth, etc.)?
- How should we handle versioning of uploaded CodeSystems?