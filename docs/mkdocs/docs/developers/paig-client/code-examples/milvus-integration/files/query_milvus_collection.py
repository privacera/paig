import os
import sys

from pymilvus import Collection, connections
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")


###################################
# HELPER FUNCTIONS
###################################

# Function to generate embedding using OpenAI
def generate_embedding(text):
    response = client.embeddings.create(input=[text],
                                        model="text-embedding-ada-002")
    return response.data[0].embedding


# Function to query OpenAI's language model for a response based on retrieved vectors
def ask_openai_for_response(records, user_question):
    # Construct a prompt by summarizing the text field of the top 5 records
    prompt = "Here are the details of recent sales transactions:\n\n"

    for record in records[0]:
        text = record.text
        metadata = record.metadata
        sales_person = metadata.get("sales_person")
        country = metadata.get("country")

        prompt += f"- {text} (Salesperson: {sales_person}, Country: {country})\n"

    prompt += ("\nBased on this information, please answer below question, "
               "don't make up things if you don't know the answer.")

    prompt += "\n\nQuestion: " + user_question

    # Query OpenAI
    response = client.chat.completions.create(model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0)

    return response.choices[0].message.content.strip()


# Function to format and print the records in a tabular format
def print_results_in_table(results):
    print(f"{'ID':<2} {'Text':<25} {'Users':<20} {'Groups':<20} {'Metadata':<50}")
    print("-" * 130)

    i = 0
    for result in results[0]:
        i += 1
        id = str(i)
        text = result.text[:20] + "..." if len(result.text) > 20 else result.text
        users = ', '.join(result.users)
        groups = ', '.join(result.groups)
        metadata = result.metadata

        print(f"{id:<2} {text:<25} {users:<20} {groups:<20} {str(metadata):<50}")


# Function to search and query the collection
def search_and_query(text, expression=None):
    # Generate the embedding for the question
    question_embedding = generate_embedding(text)

    # Perform a vector search in the collection based on the question embedding
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}, "offset": 0}
    search_results = collection.search(
        data=[question_embedding],  # The embedding vector generated from the question
        anns_field="vector",  # The field storing the vector in the collection
        param=search_params,  # Search parameters
        limit=10,  # Limit to top 10 results
        output_fields=["text", "users", "groups", "metadata", "vector"],
        expr=expression  # Optional filter expression
    )

    # Print the search results in table format
    print("Vector Search Records to be sent to OpenAI for processing:")
    print_results_in_table(search_results)

    return search_results


###################################
# MAIN CODE
###################################

MILVUS_COLLECTION_NAME = 'sales_data'

# Establish connection to Milvus
connections.connect(alias='default', host=MILVUS_HOST, port=MILVUS_PORT)

# Load the collection
collection = Collection(name=MILVUS_COLLECTION_NAME)
collection.load()

user = "testuser"
if len(sys.argv) >= 2:
    user = sys.argv[1]

# Search the collection based on a question
user_question = "What are the total units sold of our products and how much revenue was generated?"

from paig_client import client as paig_shield_client

paig_shield_client.setup(frameworks=["milvus"])

with paig_shield_client.create_shield_context(username=user):
    from paig_client.model import ConversationType
    import uuid

    thread_id = str(uuid.uuid4())

    # Calling PAIG Shield to check access, so prompt text will be logged
    paig_shield_client.check_access(
        text=user_question,
        conversation_type=ConversationType.PROMPT,
        thread_id=thread_id
    )

    # Perform the search and query
    query_results = search_and_query(user_question)

    # Ask OpenAI for a response based on the search results
    response = ask_openai_for_response(query_results, user_question)

    # Calling PAIG Shield to check access, so prompt text will be logged
    paig_shield_client.check_access(
        text=response,
        conversation_type=ConversationType.REPLY,
        thread_id=thread_id
    )

    # Print the generated response
    print("\nOpenAI's Response:")
    print(response)