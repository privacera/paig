---
title: Manage VectorDB Policies
#icon: material/checkbox-multiple-outline
---

# Manage VectorDB Policies

Managing policies for your VectorDB instances in PAIG is an essential step in ensuring data security and compliance with
your organization's data governance standards. This guide outlines the process of configuring access control and data
filtering policies for VectorDB.

## Accessing the Policy Management Page

To manage policies for VectorDB:

1. Navigate to the VectorDB policy management page within the PAIG portal.
2. Here, you'll find two primary sections: "Access Control" and "RAG Contextual Data Filtering."

## Access Control

### Purpose and Functionality

- **Purpose**: Access Control policies in VectorDB define who has the permission to access specific data chunks or
  context.
- **Functionality**: These policies are crucial for controlling access based on user or group permissions, directly
  impacting which data segments are accessible.

### Managing Access

- **User/Group-Based Access Control**: Specify which users or groups have access to certain data segments within
  VectorDB.
- **Prioritizing Security**: If there's an overlap where a user belongs to both allowed and denied groups, the system
  defaults to deny access.

## RAG Contextual Data Filtering

### Purpose and Functionality

- **Purpose**: This feature enables fine-grained filtering of data retrieved through Retrieval-Augmented Generation (
  RAG) based on user permissions.
- **Functionality**: Ensures that users only receive data they are authorized to access, enhancing data security and
  compliance.

### Managing RAG Filtering Permissions

- **Select Tag and Values**: Choose a tag and its corresponding values to define the scope of data filtering.
- **Specify Access**: Determine which users and groups should be given or denied access to the data defined by the tag
  and its values.
- **Add New Data Filtering Rule**: Utilize the "ADD DATA FILTERING" button to create new rules based on tags, values,
  and user permissions.

## Use Cases for VectorDB Policy Management in PAIG

### Use Case 1: Explicit Allow and Implicit Deny for Others

- **Scenario**: Implementing selective access control for sensitive data.
- **Rules**: Admin grants 'allow' permissions to specific users (e.g., User4) and groups (e.g., GroupC) for 'SECURITY:
  CONFIDENTIAL' tagged data.
- **Outcome**: User4 and GroupC can access confidential data during RAG retrieval. All other users and groups are
  implicitly denied access, ensuring controlled distribution of sensitive information.

### Use Case 2: Access for Everyone with Specific Denies

- **Scenario**: Broad access to certain data with exceptions.
- **Rules**: 'Everyone' is granted access to 'COUNTRY: UK', with explicit denies placed on User5 and GroupD.
- **Outcome**: General access to UK-related data is available, except for User5 and GroupD who are specifically
  restricted.

### Use Case 3: Project-Specific Data Access

- **Scenario**: Controlled data access for a new project.
- **Rules**: Project team members are explicitly allowed access to 'PROJECT: Alpha'; others are implicitly denied.
- **Outcome**: Only designated project team members can retrieve 'PROJECT: Alpha' data, while it remains inaccessible to
  non-team members.

### Use Case 4: Restricting Sensitive Data Post-Breach

- **Scenario**: Enhancing data security following a breach.
- **Rules**: 'Everyone' is allowed access to 'SECURITY: INTERNAL', but groups affected by the recent breach are
  specifically denied.
- **Outcome**: Broad internal access is maintained, but compromised groups are excluded from accessing sensitive
  internal security data.

### Use Case 5: Temporary Access Changes During Audits

- **Scenario**: Modifying access controls for an audit period.
- **Rules**: 'Everyone' is given access to 'AUDIT: Financials', except for departments under audit.
- **Outcome**: While most users can access financial audit data, the departments under review are excluded for the
  duration of the audit.

## Tips for Efficient Policy Management

- **Avoid Redundancy**: Ensure that the same sensitive data is not included in multiple filtering rules.
- **Prioritize Security**: If there's an overlap where a user belongs to both allowed and denied groups, the system
  defaults to deny access.

