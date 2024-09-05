---
title: Integrating PAIG with Milvus
---

## Prerequisites:
Before proceeding, it's crucial to confirm that your existing Milvus collection is configured with the `enable_dynamic_field` parameter set to `True` during its creation phase. If this parameter not be set, it's necessary to recreate the collection, ensuring the inclusion of the `enable_dynamic_field=True` parameter. Detailed instructions for creating a collection with this parameter enabled can be found in milvus documentation [here](https://milvus.io/docs/enable-dynamic-field.md#Enable-dynamic-field).

Once your collection is established, you gain the flexibility to integrate dynamic fields, enabling adding dynamic fields during record insertion. Let's delve into the specifics of these dynamic fields:

1. **Users**:
     - Data Type: Array
     - Description: This field houses a list of users permitted to access the current record after insertion.
     - Example: `["testuser", "ryan", "john", "bob"]`

2. **Groups**:
     - Data Type: Array
     - Description: Here lies a list of groups granted access to the current record after insertion.
     - Example: `["sales", "privacera-all", "privacera-us"]`

3. **Metadata**:
     - Data Type: JSON
     - Description: Comprising key-value pairs, this field facilitates data filtration based on defined policies within the Privacera Portal.
     - Example: `{"security": "confidential", "country": "US"}`

## Setup
The below line of the code shows how we have enabled milvus data governance by adding it to list of frameworks while
setting up privacera shield client.

```python
paig_shield_client.setup(frameworks=["milvus"])
```

!!! info "Multiple Frameworks"
    This can also be utilized in conjunction with AI application policies by incorporating it within the Langchain 
    framework as shown below: 
    ```python
    paig_shield_client.setup(frameworks=["langchain", "milvus"])
    ```
