import streamlit as st
import os
from dotenv import load_dotenv
from rag_utils import process_pdf, query_document, get_available_namespaces, clear_all_indexes

# Disable PyTorch module inspection to prevent the error
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Page configuration
st.set_page_config(
    page_title="Document Q&A System",
    page_icon="📚",
    layout="wide"
)

# Load environment variables
load_dotenv()

def main():
    st.title("Document Q&A System")
    
    # Initialize session states
    if 'namespaces' not in st.session_state:
        st.session_state.namespaces = get_available_namespaces()
    
    if 'show_clear_confirmation' not in st.session_state:
        st.session_state.show_clear_confirmation = False
    
    # Sidebar for document upload
    with st.sidebar:
        st.header("Upload Document")
        uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
        
        # Auto-generate a namespace based on the file name if provided
        default_namespace = "default"
        if uploaded_file is not None:
            default_namespace = os.path.splitext(uploaded_file.name)[0].lower().replace(" ", "_")
            
        namespace = st.text_input("Namespace", value=default_namespace, disabled=True)
        
        if uploaded_file is not None:
            if st.button("Process Document"):
                with st.spinner("Processing PDF..."):
                    # Save the uploaded file temporarily
                    with open("temp.pdf", "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Process the PDF
                    chunk_count = process_pdf("temp.pdf", namespace)
                    st.success(f"Document processed with {chunk_count} chunks and indexed in namespace: {namespace}")
                    
                    # Update namespaces in session state
                    st.session_state.namespaces = get_available_namespaces()
        
        # Add a refresh button
        if st.button("Refresh Namespaces"):
            st.session_state.namespaces = get_available_namespaces()
            st.success("Namespaces refreshed!")
            
        # Display available namespaces
        st.subheader("Available Documents")
        if st.session_state.namespaces:
            for ns in st.session_state.namespaces:
                st.write(f"• {ns}")
        else:
            st.write("No documents indexed yet")
            
        # Add a separator
        st.markdown("---")
        
        # Add a section for database management
        st.subheader("Database Management")
        
        # Toggle confirmation dialog
        if st.button("🗑️ Clear All Indexes") or st.session_state.show_clear_confirmation:
            st.session_state.show_clear_confirmation = True
            
            st.warning("⚠️ This will delete all indexed documents. This action cannot be undone.")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Yes, Clear All", key="confirm_yes"):
                    with st.spinner("Clearing all indexes..."):
                        success = clear_all_indexes()
                        if success:
                            st.success("All indexes have been cleared successfully!")
                            # Update namespaces in session state
                            st.session_state.namespaces = get_available_namespaces()
                            # Hide confirmation dialog
                            st.session_state.show_clear_confirmation = False
                            st.experimental_rerun()
                        else:
                            st.error("Failed to clear indexes. Please try again.")
            
            with col2:
                if st.button("❌ Cancel", key="confirm_no"):
                    st.session_state.show_clear_confirmation = False
                    st.experimental_rerun()
    
    # Main area for asking questions
    st.header("Ask Questions About Your Document")
    
    # If no namespaces are available, show a message
    if not st.session_state.namespaces:
        st.info("No documents have been indexed yet. Please upload a document first.")
        return
        
    # Only show the question input if namespaces are available
    selected_namespace = st.selectbox("Select document", st.session_state.namespaces, label_visibility="collapsed")
    
    # Set a fixed number of chunks to retrieve (hidden from user)
    top_k = 5
    
    question = st.text_area("Your question", height=100)
    
    if question and st.button("Ask"):
        with st.spinner("Thinking..."):
            answer = query_document(question, selected_namespace, top_k)
            
            st.subheader("Answer")
            st.markdown(answer)

if __name__ == "__main__":
    main() 