import os
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec

# Initialize Pinecone index
def init_pinecone(index_name):
    # Initialize Pinecone client
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    # Check if index exists
    existing_indexes = [index_info['name'] for index_info in pc.list_indexes()]

    # If index exists, check if dimensions match
    if index_name in existing_indexes:
        # Get index description
        index_description = pc.describe_index(index_name)
        # Check dimension
        if index_description.dimension != 1536:
            print(f"Deleting index {index_name} with incorrect dimension {index_description.dimension}")
            pc.delete_index(index_name)
            # Need to recreate the index
            existing_indexes.remove(index_name)

    # Create index if it doesn't exist or was deleted
    if index_name not in existing_indexes:
        print(f"Creating index {index_name} with dimension 1536")
        pc.create_index(
            name=index_name,
            dimension=1536,  # 1536 for ada-002
            metric="cosine",
            spec=ServerlessSpec(
                cloud='aws',      # or 'gcp' or 'azure'
                region='us-east-1'  # specify the desired region
            )
        )

    # Get the index
    index = pc.Index(index_name)
    return index


# Embed and upload to Pinecone
def upload_chunks_to_pinecone(chunks, index, namespace="default"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    for i, chunk in enumerate(chunks):
        response = client.embeddings.create(model="text-embedding-ada-002", input=chunk)
        vector = response.data[0].embedding
        index.upsert(vectors=[(f"chunk-{i}", vector, {"text": chunk})], namespace=namespace)

