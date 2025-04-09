---
title: PAIG Server 0.0.3
---

- **New Features**:  
    - Added Developer's Guide documentation.  
    - Introduced Tutorial and Integration Guide for PAIG with Milvus VectorDB.  
    - Separated Core Authorization logic into a new Python module: `paig-authorizer-core`.  
    - Integrated `paig-authorizer-core` within `paig-server`.  
    - Implemented cleanup logic in the encryptor refresher service.
- **Improvements & Updates**:  
    - Updated the **task template** to streamline issue creation.  
    - Refined default values in **Authz response** for Ranger policy IDs, Audit ID, PAIG policy IDs.
    - Refreshed the **PAIG logo and title**.  
    - Improved **audit decryption** to use the same encoding as encryption.  
    - Enhanced `README.md` with a new **animated GIF** showcasing all PAIG features.
- **Fixes**:  
    - Fixed broken notebook links in documentation.  
    - Resolved `paig-server` Python package installation issue.  

<div class="grid cards" markdown>
-  :material-page-previous: Prev topic: [Releases](../index.md#paig-server)
</div>