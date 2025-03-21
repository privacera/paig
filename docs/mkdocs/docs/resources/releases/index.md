# Release Notes  

PAIG maintains a structured release schedule to deliver continuous improvements, feature enhancements, and critical bug fixes across its core projects. Each release includes optimizations, security updates, and new capabilities to ensure a seamless experience for our users.  

## **PAIG Server**  

=== "v0.0.6 (2025-03-17)"
    - **🚀 New Features**:  
        - Introduced support for Paig Lens to enhance functionality.  
        - Updated the PAIG UI navigation bar for a better user experience.  
        - Improved support for MySQL to enhance database stability.  
    - **🔄 Improvements & Updates**:  
        - The `User Invited` column now displays `'NA'` when the invite status is unavailable.  

=== "v0.0.5 (2025-03-06)"
    - **🚀 New Features**:  
        - Added PAIG Security Evaluation feature to enhance risk assessment and compliance.
        - Added a backend API to support security guardrails.
        - Introduced Cypress tests for User & Group CURD operations to improve reliability.

=== "v0.0.4 (2025-02-24)"
    - **🚀 New Features**:  
        - Added AWS Bedrock Guardrails support for enhanced security and compliance.  
        - Improved API error handling to provide better responses for invalid API endpoints.
    - **🛠 Fixes**:  
        - Fixed application count in the Sensitive Data Access dashboard graph.

=== "v0.0.3 (2024-10-08)"
    - **🚀 New Features**:  
        - Added Developer's Guide documentation.  
        - Introduced Tutorial and Integration Guide for PAIG with Milvus VectorDB.  
        - Separated Core Authorization logic into a new Python module: `paig-authorizer-core`.  
        - Integrated `paig-authorizer-core` within `paig-server`.  
        - Implemented cleanup logic in the encryptor refresher service.
    - **🔄 Improvements & Updates**:  
        - Updated the **task template** to streamline issue creation.  
        - Refined default values in **Authz response** for Ranger policy IDs, Audit ID, PAIG policy IDs.
        - Refreshed the **PAIG logo and title**.  
        - Improved **audit decryption** to use the same encoding as encryption.  
        - Enhanced `README.md` with a new **animated GIF** showcasing all PAIG features.
    - **🛠 Fixes**:  
        - Fixed broken notebook links in documentation.  
        - Resolved `paig-server` Python package installation issue.  

=== "v0.0.2 (2024-09-06)"
    - **🚀 New Features**:  
        - Added support for OpenSearch as an audit storage backend.  
    - **🔄 Improvements & Updates**:  
        - Improved the server startup process for better performance.  
        - Reduced scanner loading time for faster execution.  
    - **🛠 Fixes**:  
        - Addressed various warnings for a cleaner runtime.  
        - Updated dependencies to improve stability and security.  

=== "v0.0.1 (2024-08-14)"
    - **🚀 New Features**: 
        - Initial release of the PAIG Server.  

## **PAIG SecureChat**

=== "v0.0.3 (2025-03-19)"
    - **🔄 Improvements & Updates**:
        - Renamed the environment variable `PAIG_API_KEY` to `PAIG_APP_API_KEY` for better clarity.

=== "v0.0.2 (2025-02-20)"
    - **🚀 New Features**:
        - Added support for Amazon Bedrock Claude models, including a sample configuration.  
        - SecureChat now includes Swagger API documentation for better API visibility.  
        - Introduced OpenAI proxy endpoint support to enhance model integration.  
        - Added support for MySQL database with API key authentication.  
        - Implemented PAIG_API_KEY support for secure API access.  
    - **🔄 Improvements & Updates**:
        - Langchain, OpenAI and Boto3 dependencies upgraded to ensure better performance and compatibility.

=== "v0.0.1 (2024-10-22)"
    - **🚀 New Features**:
        - Initial release of PAIG SecureChat.

## **PAIG Client Releases**

=== "v0.0.4 (2025-03-18)"
    - **🔄 Improvements & Updates**:
        - Renamed the environment variable `PAIG_API_KEY` to `PAIG_APP_API_KEY` for better clarity.

=== "v0.0.3 (2025-02-07)"
    - **🚀 New Features**:
        - Added support for `PAIG_API_KEY` to enable secure authentication and seamless integration with the PAIG server.

=== "v0.0.2 (2024-11-12)"
    - **🔄 Improvements & Updates**:
         - Enhanced README documentation for better usability and understanding.

=== "v0.0.1 (2024-09-06)"
    - **🚀 New Features**:
        - Initial release of the PAIG Client.

