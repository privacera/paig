---
title: Integrating PAIG with VectorDB
icon: material/vector-combine
---

In the technical integration of VectorDB with PAIG, a key aspect is the preservation and enforcement of original access
policies directly within VectorDB. This mechanism ensures that users interact only with the data for which they have
explicit access rights, mirroring the permissions set at the data source level. By embedding these access controls into
VectorDB, PAIG provides a seamless and secure data access layer, preventing unauthorized data exposure to both the
LLM and GenAI applications. By leveraging PAIG for VectorDB, organizations can ensure robust
security and governance over their diverse data sources, including Confluence Wiki pages, databases, documents, and
support tickets

The integration of PAIG with VectorDB is designed to address the following key requirements:

1. **Carrying Forward Access Controls**: Ensuring that the original data source’s access policies are maintained and
   applied within VectorDB. This includes user and group permissions, along with any metadata-based access conditions.

2. **Filtering at the VectorDB Level**: Implementing data access filters directly in VectorDB. This step is crucial for
   maintaining data privacy and compliance, as it restricts data availability to the GenAI applications and the
   underlying LLM based on the user’s access rights.

3. **Ensuring Compliance and Security**: The integration respects and upholds data governance standards, such as GDPR
   and CCPA, by ensuring that data is accessed and processed in compliance with regulatory requirements and
   organizational policies.


The [User Guide](../../user-guide/securing-vectordb.md) provides additional details and use cases of the integration.

## Security Columns

PAIG enhances the security and governance of VectorDB by utilizing additional columns specifically designed to manage
access permissions and enforce sophisticated access control mechanisms. These columns are instrumental in reflecting the
permissions from the original data sources into VectorDB, ensuring a seamless and secure data governance framework.
Below is an update on how these columns are utilized:

- **Users**: This column is dedicated to specifying the individual users who are granted access to a particular data
  record. By listing user identifiers, PAIG can directly control which users can view or interact with specific segments
  of data, providing a user-level granularity in access control.

- **Groups**: Similar to the 'Users' column, the 'Groups' column identifies the groups or teams within an organization
  that are authorized to access certain data records. This allows for broader access control policies that align with
  organizational roles and hierarchies, simplifying management of access permissions at a group level.

- **Metadata**: The 'Metadata' column is a flexible and powerful tool for implementing tag-based and attribute-based
  access control. It stores additional key-value pairs related to the data record, enabling administrators to define
  access controls based on specific criteria. Some common attributes include:

    - **Security**: This attribute indicates the privacy level of the record, such as 'Confidential', 'Public', or '
      Internal'. By categorizing data based on its sensitivity, PAIG can enforce appropriate access controls, ensuring
      that sensitive information is only accessible to authorized users.

    - **Country**: This attribute specifies the country associated with the customer or data record, such as 'US', 'UK',
      or 'CA'. This enables geographic-based access controls, allowing organizations to comply with regional data
      protection regulations and policies by controlling access based on the user's or data's geographic location.

---
:octicons-tasklist-16: **What Next?**

<div class="grid cards" markdown>

-   :material-book-open-page-variant-outline: __Read More__

    [User Guide](../../user-guide/securing-vectordb.md)

-   :material-lightning-bolt-outline: __How To__

    [Manage VectorDB Policies](../../user-guide/manage-vectordbs/vectordb-policies.md)
