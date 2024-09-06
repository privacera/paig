---
title: Manage GenAI Application Policies
#icon: material/checkbox-multiple-outline
---

# Manage GenAI Application Policies

Managing policies for your GenAI application in PAIG is a crucial step in ensuring the application operates securely and
in accordance with your organization's data governance standards. This guide will walk you through the process of
managing access and content restriction policies.

## Accessing the Policy Management Page

Navigate to the policy management page for your GenAI application. Here, you will find two main sections: Access Control
and Content Restriction.

## Access Control

- **Purpose**: Access Policies determine who can or cannot use the GenAI application. They are essential for controlling user and group access to the application.
- **Functionality**: These policies allow or deny application access to specific users or groups. For instance, you might allow access to certain departments while restricting others.
- **Management**: On the policy management page, you will find options to add users or groups to either 'Allow Access' or 'Deny Access' lists. If a user is listed in both, they will be denied access by default, prioritizing security.

### Allow and Deny Access

- **Allow access to AI Application for Users/Groups**: This row lists all users and groups who are currently granted access to the GenAI
  application.

- **Deny access to AI Application for Users/Groups**: Here, you will see the users and groups who are denied access.

!!! tip "Overlapping Access"

    If a user appears in both the **Allow** and **Deny** lists, either directly or via group membership, access for that 
    user will default to 'Deny'. This ensures a conservative approach to access management.

## Content Restriction

- **Purpose**: Content Restriction Policies govern how the application handles sensitive content within prompts, responses, and conversation histories, as well as intermediate context derived from RAG (Retrieval-Augmented Generation).
- **Functionality**: These policies are dynamic and context-sensitive. They apply based on the actual content of user interactions and the data processed by the AI model. For example, a policy might redact sensitive personal information from a conversation or block certain types of queries based on their content.
- **Management**: In the Content Restriction section, admins can activate or deactivate predefined restrictions, as well as create new ones. Each restriction can be configured with specific actions (allow, deny, redact) and linked to sensitive data types, which can be selected from the 'Sensitive Data' dropdown in the Account section.

This section comes with predefined content restrictions that admins can enable or disable as needed.

### Managing Restrictions

- **Restriction Rows**: Each row represents a specific restriction, detailing its description, the affected
  users/groups, the sensitive data involved, and the restriction actions (allow, deny, redact) for both prompts and
  replies.

- **Enabling/Disabling Restrictions**: Admins can easily toggle each restriction on or off, customizing the
  application’s behavior to fit specific security and privacy needs.

### Adding New Restrictions

- Click on the ==**ADD RESTRICTION**== button located at the top right of the section to introduce new restrictions.
- Fill in the necessary details including description, affected users/groups, sensitive data (selected from a dropdown
  list available in the Account -> Sensitive Data page), and the restriction actions.

!!! tip "Duplicate Sensitive Data"

    The same sensitive data cannot be included in multiple restriction rows to prevent conflicts and redundancy.


### Special Group: "Everyone"

- The “Everyone” group is a unique identifier that includes all users. When used in a restriction, it applies the rule
  universally across the user base.
