# paig-server Changelog
All changes to paig-server will be documented in this file.

## [v0.0.11] - 2025-07-14
### Added
  - Configurable concurrent run limit for evaluations.
  - Validation checks to prevent creation of duplicate evaluation configs and reports.
  - Completion time display on the evaluation report detail page.
  - Categories count on the evaluation config page with clickable popup showing category type details.
  - Get Categories API with type support integrated into evaluation config.
  - Added evaluation target application connection check.
  - Unique constraints added on eval-config, eval-config-history, and eval-report name columns.
  - Enhanced audit context with detailed guardrail information, including name, tags, and associated policies.

### Changed
  - Updated README.md with PowerShell and Git Bash setup instructions.
  - Made the evaluation verbose flag configurable.
  - Updated base versions of paig-authorizer-core and paig-evaluation dependencies.
  - Refactored evaluation service to support tenant ID.
  - Improved validation for evaluation target API schema.
  - Synchronized guardrail details between test input screen API and audit context.
  - Handle custom exceptions in shield

### Fixed
  - Resolved duplication issue in evaluation reports.
  - Corrected evaluation category severity count when running across multiple target applications.
  - Fixed paginated response error when request size is zero.
  - Added keep-alive timeout for Uvicorn to prevent "connection reset by peer" errors.
  - Removed repeated instructions from CONTRIBUTING.md to improve clarity.



## [v0.0.10] - 2025-04-21
### Added
- PAIG now provides a dynamic way to fetch application configurations using API keys, removing the need for manual file downloads and making the process faster and more efficient. 
- Users can:
    - Generate application-specific API keys in the PAIG server.
    - Use API keys to fetch configurations securely, without manual steps.
    - Pass the API key either as an env variable or embed it directly in the application code.
    - Manage API key validity and status directly from the PAIG server.


## [v0.0.9] - 2025-04-16
### Added
- Added predefined response templates for guardrails configuration
- Implemented Tenant ID support in guardrail system

### Changed
- Fixed MySQL database compatibility issues in guardrail functionality


## [v0.0.8] - 2025-04-09
### Added
- Enhanced PAIG evaluation
    - Improved user interface for PAIG evaluation results
    - Detailed breakdown of evaluation metrics and category-wise performance
    - Support for different authorization methods for authentication with application under evaluation


## [v0.0.7] - 2025-04-02
### Added
- Enhanced Guardrail Functionality
    - Independent guardrail creation and application association capabilities
    - AWS Bedrock Guardrails integration with full UI support
    - Improved guardrail management interface with streamlined workflows
- Added comprehensive Cypress test suite for guardrail features

## [v0.0.6] - 2025-03-17
### Added
- Paig lens support added. PAIG UI navigation bar updated.
- Mysql compatibility improved.

### Changed
- UI Change - User Invited column updated to 'NA' in User Management

## [v0.0.5] - 2025-03-06
### Added
- Paig-eval Frontend and Backend implementation.
- Backend API for guardrails service.
- UI Cypress automation tests for User and Login operations.

## [v0.0.4] - 2025-02-24
### Added
- AWS Bedrock guardrails support.
- API Error Handling improved for invalid API endpoints.
- Fixed application count in Sensitive Data Access dashboard graph.

## [v0.0.3] - 2024-10-08
### Added
- Added documentation for Developers Guide.
- Added Tutorial and Integration Guide for PAIG with Milvus VectorDB.
- Separated Core Authorization logic into paig-authorizer-core python module.
- Integrated paig-authorizer-core python module within paig-server.
- Added cleanup logic in encryptor refresher service.

### Changed
- Updated task template to create issues.
- Updated default value in authz response ranger policy ids, audit id and paig policy ids.
- Updated PAIG logo and Title.
- Fixed notebooks link in documents.
- Fixed paig-server python package installation issue.
- Updated audits decryption to use the same encoding as used in encryption.
- Updated README.md with new animated gif with all the features of PAIG.

## [v0.0.2] - 2024-09-06
### Added
- For audit storage Opensearch support added

### Changed
- Improved server startup experience
- Fixed warnings
- Updated dependencies
- Scanner loading time improved


## [v0.0.1] - 2024-08-14
### Added
- Initial release of the `paig-server`.