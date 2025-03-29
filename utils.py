from unstructured.partition.pdf import partition_pdf

# Read PDF
def extract_text_from_pdf(pdf_path):
    elements = partition_pdf(filename=pdf_path)
    return "\n\n".join([el.text for el in elements if el.text is not None])

# Split text
def split_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks