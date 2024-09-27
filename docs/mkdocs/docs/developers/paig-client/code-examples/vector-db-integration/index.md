---
title: Vector DB Integration
---

## Securing Vector DB Searches with Metadata Filtering

In the world of Large Language Models (LLMs), vector databases are essential for expanding the use of LLMs with various types of data, including your own. A key feature of vector databases is their ability to perform fast and accurate similarity searches on vector embeddings from both unstructured and structured data. This capability is ideal for providing real-time context to LLMs, enabling them to make more relevant inferences. 

Typically, each row in the VectorDB consists of a vector, which is a numerical representation, text or chunk, and additional metadata. Metadata could include the source of the data or other attributes that describe the content.

In this document, we will explain how additional metadata can be added to vectors and used to filter content that users do not have permission to access. This metadata could include permissions from the original document or its classification. This approach is ideal for preventing data leakage and enforcing compliance policies such as GDPR, CCPA, and HIPAA.

### What is Metadata Filtering in Vector Search?
Let's first understand how a vector databases works. When you want to search through large amounts of data, the data is first processed through something called an embedding model. This model converts raw data (like text, images, or other types of information) into a vector embedding—a list of numbers that represents the data. These vector embeddings capture key features and relationships of the original data in a more compact, mathematical form.

For example, if we take product descriptions from an e-commerce platform and pass them through an embedding model, the descriptions are converted into vectors of numbers that represent the essence of the product's content (e.g., specifications, features). These vectors are then stored in the vector database alongside metadata like product name, category, price, manufacturer, and country of origin. This metadata provides additional context that can be used to refine searches or enforce access controls.

#### How Vector Search Works
Once all your product data is stored as vector embeddings in the vector database, you can query the database using a natural language search (e.g., "best 4K TVs under $1000"). This query is also converted into a vector, called the query vector. The vector search then compares this query vector to all the stored product vectors and retrieves the ones most similar to it.

#### Metadata Filtering
In vector searches, metadata filtering allows you to narrow down your search results based on specific criteria. For example, if you have a database of products, you can filter by metadata such as "category" or "country of origin" before the similarity search begins. This ensures that the search only compares your query to vectors that meet these filter criteria, speeding up the search process and enhancing relevance.

Think of it like a SQL "WHERE" clause. Instead of searching the entire product catalog, you can say, "Only search for products in the 'Electronics' category and available in the USA." This dramatically reduces the amount of data the system needs to process, making the search faster, more efficient, and focused on authorized data access.

### Example: Securing Product Data with Metadata Filtering

Imagine you have a vector database that contains product information for an e-commerce platform. Each product has metadata such as:

- **Product ID:** 12345
- **Name:** Ultra HD Smart TV
- **Category:** Electronics
- **Price:** $999
- **Country of Origin:** USA
- **Stock Availability:** [Vector representation of stock levels and distribution]

Now, let’s say a user in a specific role (e.g., a regional manager for the USA) needs to search for products only available in the USA. To enforce access control, we want to ensure that users can only retrieve data relevant to their region. PAIG makes it easy to apply metadata-based filters that ensure unauthorized users can’t access sensitive product information for other regions.

Here’s an example of how metadata filtering can be applied:

```python
# Search query specifying the query vector, top 5 results, and metadata filters
# Only search for products available in the USA and from the "Electronics" category
table.search(
  query_vector, 
  n=5, 
  filter=[("=", "CountryOfOrigin", "USA"),("=", "Category", "Electronics")]
)
```

In this query, the system will only retrieve data on electronics available in the USA, preventing users from accessing data outside their authorized region.

#### Benefits of Metadata Filtering for Security

In this case, the user performing the search is restricted to products available in their authorized region—"USA"—due to the metadata filtering applied by PAIG. PAIG’s authorization framework ensures that any user outside the authorized region (e.g., users from Europe or Asia) would be automatically blocked from accessing this data, thereby maintaining data confidentiality.

By applying these filters:

- **Authorized users** will receive results limited to the USA, keeping access secure and region-specific.
- **Unauthorized users** (those who shouldn’t see USA-based products) are restricted by default, ensuring that sensitive product data isn't exposed to unintended individuals.

## Benefits on Integrating Vector DB with PAIG

By leveraging PAIG, we can eliminate the manual process of managing which users or groups have access to specific records and determining which filters should be applied during searches. In traditional systems, developers often have to build and maintain complex access control mechanisms, which can be cumbersome and error-prone. With PAIG, this burden is removed, as the platform automatically enforces access control policies and applies the correct filters based on each user’s role, permissions, and contextual data.

PAIG provides an intuitive interface and powerful filtering capabilities, ensuring that users only access the data they are authorized to view. This not only simplifies the development and management of data access policies but also strengthens security and compliance by automating the enforcement of these rules. By using PAIG, organizations can focus on their core business logic, leaving the complexities of data access control, filtering, and governance to a system designed to handle these requirements efficiently and securely.

---
:octicons-tasklist-16: **What Next?**

<div class="grid cards" markdown>

-   :material-book-open-page-variant-outline: __Read More__

    [Mivus Integration Sample Tutorial](../milvus-integration/a-sample-tutorial.md)

</div>