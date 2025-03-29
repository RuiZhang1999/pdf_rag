# Document Q&A System

A Streamlit application that allows users to upload PDF documents, process them, and ask questions about their content using RAG (Retrieval-Augmented Generation) technology.

## Features
- PDF document upload and processing
- Vector storage using Pinecone
- Natural language question answering with OpenAI's GPT-4o
- Multiple document management with namespace support
- Clean and intuitive user interface

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root directory with the following keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   ```
4. Set up a Pinecone account and create a serverless index (AWS)

## How to Run

### Run Single Test
To run a simple test of the system:
```
python main.py
```

### Run Streamlit Web Application
To run the interactive web application:
```
streamlit run streamlit_app.py
```

## Usage
1. Start the Streamlit application
2. Upload a PDF document using the sidebar
3. The document will be automatically assigned a namespace based on its filename
4. Click "Process Document" to extract, chunk, and index the document content
5. Select the document from the dropdown menu in the main area
6. Type your question and click "Ask"
7. View the AI-generated answer based on the document content
