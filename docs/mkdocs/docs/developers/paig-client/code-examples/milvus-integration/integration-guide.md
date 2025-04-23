---
title: Milvus Integration Guide
---

# Milvus Integration Guide

## Prerequisites:

### 1. Configuring Milvus Collection with Dynamic Fields:
It's crucial to confirm that your existing Milvus collection is configured with the `enable_dynamic_field` parameter set to `True` during its creation phase. 
If this parameter is not set, it's necessary to recreate the collection, ensuring the inclusion of the `enable_dynamic_field=True` parameter. 

```python hl_lines="4"
schema = CollectionSchema(
    fields=[source, text, pk, vector],
    description="example_collection",
    enable_dynamic_field=True
)
```

Detailed instructions for creating a collection with this parameter enabled can be found in milvus documentation [here](https://milvus.io/docs/enable-dynamic-field.md#Enable-dynamic-field).

### 2. Adding Authorization Metadata Fields:
!!! Note "Who Should Perform This Step?"
    If the `enable_dynamic_field` parameter has not been enabled for your collection, and you prefer not to enable it, 
    you may manually add the following authorization metadata fields to your collection schema.
```python
users = FieldSchema(name="users", dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_length=65535, max_capacity=1024)
groups = FieldSchema(name="groups", dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_length=65535, max_capacity=1024)
metadata = FieldSchema(name="metadata", dtype=DataType.JSON)
```

### 3. Inserting Data with Authorization Metadata Fields:
For authorization purposes, it's essential to include the authorization metadata fields with appropriate values for each record while inserting data for each record.
Below is an example snippet of inserting data with the authorization metadata fields:

Each field has its own significance:

- `users`: Contains a list of users permitted to access the current record.
- `groups`: Contains a list of groups granted access to the current record.
- `metadata`: Comprises key-value pairs, facilitating data filtration based on defined policies within the Portal.

```python
milvus_client.insert(collection_name="example_collection", data=[
    {"source": "demo.txt", "text": "Hello World!", "vector": [0.1, 0.2, 0.3], "users": ["sally", "ryan", "john", "bob"], "groups": ["sales", "hr", "finance"], "metadata": {"security": "confidential", "country": "US"}}
])
```
Detailed instructions for inserting data with dynamic fields can be found in milvus documentation [here](https://milvus.io/docs/enable-dynamic-field.md#Insert-dynamic-data).

## Setup

### 1. Create Vector DB

Log in to the PAIG portal and navigate to **Paig Navigator > VectorDB**. Click the **CREATE VECTOR DB** button in the top right corner. Select **Milvus** as the type and complete the required details to create a new VectorDB.

!!! info "**Enable User/Group Access-Limited Retrieval** (Optional)" 
    Once the Vector DB is created, go to the **Permissions** tab and enable the **User/Group Access-Limited Retrieval** option. 
    This ensures that only authorized users and groups can retrieve data from the Vector DB, based on the users and groups specified in each record of the Milvus collection.

### 2. Create AI Application

Navigate to **Paig Navigator > AI Application** and click the **CREATE APPLICATION** button in the top right corner. Fill in the required details and, under **Associated VectorDB**, 
select the VectorDB created in the previous step to link the application with the VectorDB.

### 3. Generate AI application API Key

--8<-- "docs/integration/snippets/paig_apikey_generate.md"

### 4. Set the PAIG API Key

To initialize the PAIG Shield library in your AI application, export the __PAIG_APP_API_KEY__ as an environment variable.

```shell
export PAIG_APP_API_KEY=<API_KEY>
```

!!! note "Alternative Method: Pass API Key in Code"
    If you prefer not to use environment variables, you can directly pass the API key when initializing the library:
        ```python
        paig_shield_client.setup(frameworks=[], application_config_api_key="<API_KEY>")
        ```
    For a complete code example showing where to place this, locate the `setup()` method in the provided [sample code](#sample-code) section below.

!!! info "Precedence Rule"
    If the __PAIG_APP_API_KEY__ is set both as an environment variable and in the code, the key specified in the code will take priority.

### 5. Initialize PAIG Client

To enable data filter for Milvus in your application, include the following code snippet during the application's startup phase. 
This ensures that data filter policies are consistently enforced throughout the application's lifecycle.

The code below initializes the Privacera Shield client and configures it to work with Milvus:
```python
from paig_client import client as paig_shield_client

paig_shield_client.setup(frameworks=["milvus"])
```

!!! info "Multiple Frameworks"
    This can also be utilized in conjunction with AI application policies by incorporating it within the Langchain framework, as demonstrated below:
    ```python
    from paig_client import client as paig_shield_client

    paig_shield_client.setup(frameworks=["langchain", "milvus"])
    ```

## Usage

### 1. Define Metadata

In the PAIG portal, go to **Account > Vector DB Metadata**. Click the plus icon to add the metadata fields you want to use for data filtering. 
For example, as shown in the setup section:

```json
"metadata": {"security": "confidential", "country": "US"}
```

In this case, the metadata fields are "security" and "country," with "confidential" and "US" as their respective values.

After creating the metadata fields, you can select a field and assign values by clicking on **ADD VALUE**. These fields and values can later be referenced in policies.

### 2. Define Policies

In the PAIG portal, go to **Paig Navigator > VectorDB**. Select the VectorDB created earlier and navigate to the **Permissions** tab.

Under the **RAG Contextual Data Filtering** section, click the **ADD DATA FILTERING** button to create a new policy. 
Define the policy using the metadata fields and values you configured.

### 3. Apply and Test Data Filters in Milvus Operations

To ensure that data filter policies are enforced during interactions with Milvus, wrap your Milvus operations within the context of the Privacera Shield client. This can be done using the `create_shield_context` method, as shown below, ensuring that all operations adhere to data filter policies for the specified user.

```python
with privacera_shield_client.create_shield_context(username=user):
    # Your Milvus operation here
```

To test the integration, perform a Milvus operation within this context. The data filtering policies will be enforced, and you will only see data that complies with the defined policies.

### 4. Monitor and Audit

To monitor and audit data access and retrieval operations, go to the **Paig Lens > Access Audits** section in the PAIG portal. 
Click on the **More Details** link for the most recent audit record to view the actual filter expression applied during data retrieval from Milvus.