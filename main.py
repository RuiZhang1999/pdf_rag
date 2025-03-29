import os
from rag_utils import process_pdf, query_document

def main():
    process_pdf("./pdf/test.pdf", namespace="my_pdf")

    answer = query_document("What is this document about?", namespace="my_pdf")
    print(answer)

if __name__ == "__main__":
    main()
    
