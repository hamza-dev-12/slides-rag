# Motivation
Knowledge-based applications, particularly those utilizing Retrieval-Augmented Generation (RAG) models, have gained significant popularity due to their versatility and wide range of use cases. Inspired by this, I created a fun and practical project that leverages a RAG pipeline for academic slide presentations. Often, students rely on slides provided by instructors for exam preparation, but finding specific information in large slide decks can be time-consuming and frustrating. To address this, I developed an easy-to-use application that allows users to input the path to a PDF file and directly query its contents. Instead of manually searching through slides, users can instantly retrieve relevant information. Additionally, the application's integration with a large language model enriches the generated responses, making the information clearer and more digestible for better understanding.

# Technologies 
- Fast-API
- llama-index
- HuggingFaceEmbeddings
- Gemini
- python-3.11

# Start the application
You can start the application simply by `sudo docker compose up --build`

There are 2 pages basically one for `query` and other for `ingesting` pdf slides. In the ingesting page you can simply provide the `pdf-file-path` to ingest those documents. In the query page you can simple submit your `query` in the text-box
