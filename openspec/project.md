# Project Context

## Purpose
The psgc-script project processes Philippine Standard Geographic Code (PSGC) data from the official quarterly publications. The system handles data extraction, transformation, and validation of geographic codes and names for Philippines administrative divisions including regions, provinces, cities, municipalities, and barangays. It uses OpenSpec for specification-driven development to ensure data accuracy and systematic change management.

## Tech Stack
- Python (for data processing and ETL operations)
- OpenSpec (specification-driven development framework)
- Pandas (for data manipulation)
- openpyxl/xlsx (Excel file processing)
- Markdown-based documentation conventions
- Bash/command-line tools (for automation and scripting)

## Project Conventions

### Code Style
- Use descriptive variable names for geographic entities (e.g., region_code, municity_name)
- Follow Python PEP 8 guidelines for formatting
- Use kebab-case for file and directory names in OpenSpec changes
- Write clear, concise comments explaining data transformation logic
- Maintain consistent naming conventions for PSGC elements (region, province, municity, barangay)

### Architecture Patterns
- Specification-driven development using OpenSpec methodology
- Separation of concerns between data parsing, validation, and output generation
- Delta-based change management following OpenSpec conventions
- Capability-focused organization of functionality

### Testing Strategy
- Validate data integrity against official PSGC publications
- Unit tests for data transformation functions
- Integration tests for full ETL pipeline
- Cross-reference with previous quarters to detect unexpected changes
- Boundary checks for geographic code ranges

### Git Workflow
- Feature branch model for new capabilities
- OpenSpec change proposals required for significant modifications
- Verb-led branch names (e.g., `add-validation-rules`, `update-data-source`)
- Conventional commit messages aligned with OpenSpec change IDs
- Pull requests must reference associated OpenSpec change

## Domain Context
- PSGC: Philippine Standard Geographic Code, updated quarterly by PSA
- Geographic hierarchy: Region → Province/City → Municipality → Barangay
- Each geographic unit has a unique 9-digit PSGC code
- Geographic names may change due to legislation, plebiscites, or administrative decisions
- Official data published by Philippine Statistics Authority (PSA)

## Important Constraints
- Data accuracy is critical as PSGC is used for official statistics
- Changes must align with official PSA publications
- Backward compatibility required for existing code references
- Compliance with Philippine government data standards
- Regular quarterly updates following PSA releases

## External Dependencies
- Quarterly PSGC publication files from Philippine Statistics Authority
- Excel files containing official geographic codes and names
- Historical PSGC data for change tracking
- OpenSpec tooling for change management
