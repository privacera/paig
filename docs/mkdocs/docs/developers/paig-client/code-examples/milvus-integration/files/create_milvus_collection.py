from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection
)
import os

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")

# Connect to Milvus
connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)

# Define the schema for the collection
fields = [
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1536),
    FieldSchema(name="users", dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_length=65535, max_capacity=1024),
    FieldSchema(name="groups", dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_length=65535, max_capacity=1024),
    FieldSchema(name="metadata", dtype=DataType.JSON)
]

# Create the collection schema
collection_schema = CollectionSchema(fields, description="Sales data")

# Create the collection
collection_name = "sales_data"
collection = Collection(name=collection_name, schema=collection_schema, drop_collection=True)

# Sample data
sales_transaction_data = [
    {
        "source": "Sales Transactions",
        "text": "Sold 500 units of premium laptops to TechCorp for $250,000 on March 15, 2024. The deal was finalized during a tech conference.",
        "vector": [0.23, -0.34, 0.45, ..., 0.12],
        "users": ["emily", "john"],
        "groups": ["revenue_management"],
        "metadata": {
            "sales_person": "Emily Davis",
            "country": "US",
            "department": "Sales"
        }
    },
    {
        "source": "Sales Transactions",
        "text": "Sold 200 units of high-end smartphones to GlobalTech Ltd for $100,000 on March 20, 2024. The sale was part of a promotional event.",
        "vector": [0.15, 0.27, -0.56, ..., -0.24],
        "users": ["michael", "john"],
        "groups": ["revenue_management"],
        "metadata": {
            "sales_person": "Michael Johnson",
            "country": "US",
            "department": "Sales"
        }
    },
    {
        "source": "Sales Transactions",
        "text": "Sold 150 units of office furniture to CorporateSpaces Ltd for $75,000 on March 22, 2024. The sale included additional discounts for bulk purchase.",
        "vector": [0.34, -0.23, 0.46, ..., -0.14],
        "users": ["sarah", "rebecca"],
        "groups": ["revenue_management"],
        "metadata": {
            "sales_person": "Sarah Lee",
            "country": "UK",
            "department": "Sales"
        }
    },
    {
        "source": "Sales Transactions",
        "text": "Sold 300 units of ergonomic chairs to OfficeWorks Ltd for $90,000 on March 25, 2024. The transaction included setup and delivery services.",
        "vector": [0.19, 0.32, -0.42, ..., 0.21],
        "users": ["james", "rebecca"],
        "groups": ["revenue_management"],
        "metadata": {
            "sales_person": "James Brown",
            "country": "UK",
            "department": "Sales"
        }
    },
    {
        "source": "Sales Transactions",
        "text": "Sold 400 units of advanced software licenses to InnovateInc for $160,000 on March 30, 2024. The deal included annual maintenance support.",
        "vector": [0.28, -0.11, 0.58, ..., -0.19],
        "users": ["robert", "john"],
        "groups": ["revenue_management"],
        "metadata": {
            "sales_person": "Robert Green",
            "country": "US",
            "department": "Sales"
        }
    },
    {
        "source": "Sales Transactions",
        "text": "Sold 100 units of industrial printers to PrintMasters Ltd for $50,000 on March 28, 2024. The sale included extended warranty options.",
        "vector": [0.10, 0.46, -0.34, ..., 0.25],
        "users": ["laura", "rebecca"],
        "groups": ["revenue_management"],
        "metadata": {
            "sales_person": "Laura White",
            "country": "UK",
            "department": "Sales"
        }
    }
]

# Generate embeddings using OpenAI
def generate_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return response.data[0].embedding

# Generate embeddings for the text field in sales transaction data
embeddings = [generate_embedding(transaction["text"]) for transaction in sales_transaction_data]
sales_data_with_embeddings = [
    {**transaction, "vector": emb} for transaction, emb in zip(sales_transaction_data, embeddings)
]

# print(sales_data_with_embeddings[0].keys())

# Insert data into the collection
collection.insert(sales_data_with_embeddings)

print("Collection created and data inserted successfully.")

index_params = {
    "index_type": "HNSW",
    "metric_type": "L2",
    "params": {
        "M": 10,
        "efConstruction": 8
    }
}

collection.create_index(
    field_name="vector",
    index_params=index_params,
    index_name="sales_data_index"
)

print("Collection index created successfully.")

# Load the collection
collection.load()