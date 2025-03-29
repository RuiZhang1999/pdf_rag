import os
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
from utils import extract_text_from_pdf, split_text
from pc import init_pinecone, upload_chunks_to_pinecone
# Load environment variables
load_dotenv()

# Initialize OpenAI & Pinecone
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "rag"
index = init_pinecone(index_name)

def clear_all_indexes():
    """
    Clear all data from all namespaces in the Pinecone index
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get all namespaces
        stats = index.describe_index_stats()
        namespaces = list(stats.get("namespaces", {}).keys())
        
        # Delete vectors from each namespace
        for namespace in namespaces:
            index.delete(delete_all=True, namespace=namespace)
            
        return True
    except Exception as e:
        print(f"Error clearing indexes: {e}")
        return False

def get_available_namespaces():
    """
    Get all available namespaces from Pinecone
    
    Returns:
        list: List of available namespaces
    """
    try:
        # Get statistics about the index to retrieve namespaces
        stats = index.describe_index_stats()
        namespaces = list(stats.get("namespaces", {}).keys())
        
        # If no namespaces are found, return a default list
        if not namespaces:
            return ["default"]
            
        return namespaces
    except Exception as e:
        print(f"Error getting namespaces: {e}")
        return ["default"]

def process_pdf(pdf_path, namespace="default"):
    """
    Process a PDF file and upload chunks to Pinecone
    
    Args:
        pdf_path (str): Path to the PDF file
        namespace (str): Namespace to store the vectors
    """
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Split text into chunks
    chunks = split_text(text)
    
    # Upload chunks to Pinecone
    upload_chunks_to_pinecone(chunks, index, namespace=namespace)
    
    return len(chunks)

def query_document(question, namespace="default", top_k=5):
    """
    Query the document with a question
    
    Args:
        question (str): The question to ask
        namespace (str): Namespace to query
        top_k (int): Number of relevant chunks to retrieve
        
    Returns:
        str: Answer to the question
    """
    # Generate embedding for the question
    response = client.embeddings.create(model="text-embedding-ada-002", input=question)
    query_vector = response.data[0].embedding

    # Query Pinecone for relevant chunks
    results = index.query(vector=query_vector, top_k=top_k, include_metadata=True, namespace=namespace)
    relevant_chunks = [match["metadata"]["text"] for match in results["matches"]]

    # Construct context from relevant chunks
    context = "\n\n---\n\n".join(relevant_chunks)
    prompt = f"Please answer the question based on the following document content:\n\n{context}\n\nQuestion: {question}\nAnswer:"

    # Generate answer using GPT-4
    chat_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    
    return chat_response.choices[0].message.content
