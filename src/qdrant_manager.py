import os
import fitz  # PyMuPDF
import argparse
import qdrant_client 
from typing import List
from loguru import logger
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.core import StorageContext
from llama_index.core.schema import TextNode
from llama_index.core import VectorStoreIndex
from qdrant_client.http.models import VectorParams, Distance
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

load_dotenv()

class QdrantManager():
    def __init__(self):
        """
        Initializes the QdrantManager class.
        - Connects to Qdrant client.
        - Creates the collection if it does not exist.
        - Sets up the embedding model and language model.
        """
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))

        client = qdrant_client.QdrantClient(
            host = qdrant_host,
            port = qdrant_port
        )

        # client = qdrant_client.QdrantClient(
        #     host="localhost",
        #     port=6333
        # )

        self.collection_name = 'slides-rag'

        if not client.collection_exists(self.collection_name):
            logger.info('Creating Collection: ', self.collection_name)

            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )

        self.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.llm = Gemini(
            model="models/gemini-1.5-flash",
            api_key=os.getenv("GEMINI_API_KEY"),  # uses GOOGLE_API_KEY env var by default
        )

        # Override the embedding model/LLM as it uses OpenAI by default
        Settings.embed_model = self.embed_model
        Settings.llm = self.llm

        self.vector_store = QdrantVectorStore(collection_name='slides-rag', client=client)

        # Override the default vector store
        StorageContext.from_defaults(vector_store=self.vector_store)

    def load_pdf_slide(self, pdf_path: str):
        """
        Loads the content of a PDF file and splits it into pages.
        
        Arguments:
        - pdf_path (str): The path to the PDF file.

        Returns:
        - List[str]: A list of strings, each representing the text content of a page.
        """
        try:
            document = fitz.open(pdf_path)
            chunks = []
            for page_num in range(len(document)):
                page = document.load_page(page_num)
                content = page.get_text()  # Get the text content from each page
                chunks.append(content.replace('►', '').replace('●', '').replace('', '').replace('▪', ''))

            return chunks
        except Exception as e:
            raise

    def get_nodes(self, text: List[str]):
        """
        Converts a list of strings into TextNode objects and generates embeddings for each node.

        Arguments:
        - text (List[str]): A list of strings representing page content.

        Returns:
        - List[TextNode]: A list of TextNode objects with embeddings.
        """
        nodes = []

        for page_content in text:
            nodes.append(TextNode(text=page_content))

        for node in nodes:
            embeddings = self.embed_model.get_text_embedding(node.get_content())
            node.embedding = embeddings

        return nodes

    def ingest_documents(self, pdf_path):
        """
        Ingests a PDF document into the Qdrant vector store.

        Arguments:
        - pdf_path (str): The path to the PDF file.

        Returns:
        - None
        """
        try:
            chunks = self.load_pdf_slide(pdf_path=pdf_path)
            nodes = self.get_nodes(chunks)

            self.vector_store.add(nodes)

            logger.info(f'{pdf_path} document ingested successfully!')
        except Exception as e:
            raise

    def retrieve_nodes(self, query: str):
        """
        Retrieves relevant nodes from the vector store based on the query.

        Arguments:
        - query (str): The search query.

        Returns:
        - List[str]: A list of strings representing the text of the retrieved nodes with scores > 0.5.
        """
        index = VectorStoreIndex.from_vector_store(self.vector_store)
        retreiver = index.as_retriever()
        retreived_nodes = retreiver.retrieve(query)

        filtered_text = [node.text for node in retreived_nodes if node.score > 0.5]

        return filtered_text

    def query(self, query: str):
        """
        Queries the system to retrieve nodes and generate a response based on the provided context.

        Arguments:
        - query (str): The user's query.

        Returns:
        - str: The response generated by the language model.
        """
        retreived_nodes = self.retrieve_nodes(query)

        context = "\n".join(retreived_nodes)

        prompt = f"You are a chat-bot responsible for resolving user <Query> by considering the provided context.\n<Query>:{query}\n<Context>:{context}"

        response = self.llm.complete(prompt)

        return response

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Description of your script.')

    parser.add_argument('--slide_path', default=None)

    args = parser.parse_args()

    qdrant_manager = QdrantManager()

    # Uncomment to ingest documents
    # if args.slide_path:
    #     qdrant_manager.ingest_documents(args.slide_path)

    qdrant_manager.query(query="What are the major issues when signing the contract")
