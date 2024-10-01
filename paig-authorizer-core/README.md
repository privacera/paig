# paig-authorizer-core

## Overview

`paig-authorizer-core` is a Python library designed to provide a framework of interfaces and abstract classes for building custom authorization implementations. This library allows developers to define their own authorization logic while ensuring consistency and structure.

## Features

- Provides a set of interfaces and abstract classes.
- Customizable implementations for various authorization scenarios.
- Easy to extend and integrate into existing applications.

## Installation

You can install the library using pip:

```bash
pip install paig-authorizer-core
```

## Usage

To use the `paig-authorizer-core` library, follow these steps:

1. **Import the required classes**:
   ```python
   from paig_authorizer_core import BasePAIGAuthorizer
   from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
   ```

2. **Create a custom authorizer class**:
   Implement your own authorizer by extending the `BasePAIGAuthorizer` class:
   ```python
   class MyCustomAuthorizer(BasePAIGAuthorizer):
       def get_user_id_by_email(self, email: str) -> Optional[str]:
           # Implementation to retrieve user ID by email
           pass
       
       def get_user_groups(self, user: str) -> List[str]:
           # Implementation to retrieve user groups
           pass

       # Implement other abstract methods...
   ```

3. **Instantiate your custom authorizer**:
   ```python
   authorizer = MyCustomAuthorizer()
   ```

4. **Create an authorization request**:
   ```python
   authz_request = AuthzRequest(
       user_id="user@example.com",
       application_key="MyApp",
       traits=["trait1"],
       request_type="access"
   )
   ```

5. **Authorize the request**:
   Call the `authorize` method to check if the request is authorized:
   ```python
   response = authorizer.authorize(authz_request)
   print(f"Authorization response: {response}")
   ```

6. **Create a VectorDB authorization request**:
   ```python
   vector_db_request = VectorDBAuthzRequest(
       user_id="admin@example.com",
       application_key="MyApp"
   )
   ```

7. **Authorize the VectorDB request**:
   Call the `authorize_vector_db` method to check VectorDB access:
   ```python
   vector_db_response = authorizer.authorize_vector_db(vector_db_request)
   print(f"VectorDB authorization response: {vector_db_response}")
   ```
