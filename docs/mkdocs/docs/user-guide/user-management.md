---
title: Users and Groups
#icon: material/account-multiple
---

# User Management

**Introduction:**  
User Management is a crucial aspect of maintaining and operating the PAIG platform. By ensuring appropriate access, you
not only enhance platform security but also streamline tasks and responsibilities for different members of your team.

**Features and Components:**

1. **User Creation:** Learn the step-by-step process to add a new user to the PAIG platform. Assign them credentials and
   initial roles that dictate their access levels.

2. **User Roles & Permissions:** Dive deep into the different roles available in the PAIG system. Understand the
   permissions associated with each role, from those designed for view-only access to those equipped for full
   administrative capabilities.

3. **Modifying User Details:** Users evolve, and their access requirements can change. Here, we'll walk you through
   updating user profiles, changing roles, and redefining permissions as necessary.

4. **Deactivating & Deleting Users:** For those times when an account is no longer needed, whether due to role changes
   or an employee departure, you'll find instructions on how to safely deactivate or completely remove a user from the
   system.

5. **Audit & Activity Logs:** Keep track of user activities, login attempts, and more. This section aids in ensuring
   transparency and accountability for all actions taken within the platform.

**Best Practices:**  
While managing users, always ensure that the principle of least privilege is maintained. Only grant permissions that are
necessary for a user's role. Regularly review user access and make adjustments as roles within your organization evolve.


## Roles in PAIG

### Overview

To ensure a secure and tailored user experience within PAIG, we employ a role-based access control system. By doing so, we allow organizations to grant precise permissions based on users' roles. Each role is crafted to meet the requirements of different organizational personas.

### Defined Roles and Their Permissions:

- **Owner:** The most comprehensive role with overarching privileges. Owners can:
    - Manage user profiles
    - Handle applications
    - Set application policies
    - Access reports, including usage, audits, and dashboards
    - Manage user groups

- **Security Team:** Members focused on organizational security. They can:
    - Manage and view user profiles
    - Manage application policies
    - Access and view reports
    - View user and group details

- **Compliance Team:** Ensuring adherence to standards and regulations. They can:
    - Manage user profiles
    - Manage application policies
    - Access reports
    - View user and group details

- **IT Admin:** Central to tech infrastructure and support. IT Admins can:
    - Manage user profiles
    - Handle applications
    - Set application policies
    - Access reports
    - Manage and view user and group details

- **Governance:** Oversees data handling and policy adherence. Governance team members can:
    - Manage and view user profiles
    - Access reports

- **Developer:** A role tailored for those who build and maintain applications. Developers can:
    - Manage user profiles
    - Manage applications
    - Set application policies
    - Access reports

- **User:** The foundational role for regular end-users. Users can:
    - Manage and view their own profile

**Below is a simplified version of what each User Role can do within PAIG**

{{ read_csv('snippets/roles_permissions.csv') }}

### Key Features of Role-Based Access:

- **Role-specific Interface:** The PAIG interface intuitively presents options based on the logged-in user's role, ensuring an uncomplicated user experience.

- **Email Association:** For accountability and communication, all roles (excluding the standard User role) require an associated email address.

### Best Practices:

- Regularly review and update role assignments. This ensures that users have the correct permissions aligned with their responsibilities.

- Maintain open communication with users about their role-based experience. This feedback can be instrumental in refining and enhancing the system.
