---
title: Managing VectorDBs
#icon: material/application-brackets
---

# Managing VectorDBs

Managing VectorDB in PAIG is a straightforward process, enabling you to efficiently configure and control your data
sources for AI applications. This guide will walk you through viewing existing VectorDB instances and setting up a new
one.

## Accessing VectorDB Management

To manage your VectorDB instances:

1. **Navigate to VectorDB**: Select the 'VectorDB' option from the left navigation pane in the PAIG portal.
2. **View Registered Instances**: On this page, you will see a list of all VectorDB instances that are registered with
   PAIG. You can select an instance to view and manage its details or proceed to create a new one.

## Creating a New VectorDB Instance

### Steps to Create a New Instance

1. **Go to VectorDB Configuration**:
    - Navigate to `VectorDB`.
    - Click the `CREATE VECTORDB` button located at the top right. This will open a dialog box for entering the details
      of the new VectorDB instance.

2. **Fill in the Details**:

   {{ read_csv('snippets/create_vectordb_params.csv') }}

### Finalizing and Activating

- After filling in the necessary details, click ==**CREATE**== to register the new VectorDB instance in PAIG.
- Once created, you may need to configure specific settings such as data access policies or integration parameters based
  on your requirements.
