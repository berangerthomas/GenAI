import logging
import os

import chainlit as cl
import chromadb
from llama_index.core import (
    Document,
    Settings,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set working directory as the one this script is in
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Configure LlamaIndex to use HuggingFace embeddings
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Connect to existing ChromaDB database
collection_name = "genai"
chroma_client = chromadb.PersistentClient(path="chroma_db")
chroma_collection = chroma_client.get_collection(name=collection_name)

# Log the number of documents in the collection and infos about the collection
logger.info(f"Collection {collection_name} found in ChromaDB:")
data = chroma_collection.get(include=["documents", "metadatas"])
doc_count = len(data.get("documents", []))
logger.info(f"{doc_count} document(s)")

# Display IDs in the collection
ids = data.get("ids", [])
logger.info(f"  IDs: {', '.join(ids)}")

# Display metadata if available
metadatas = data.get("metadatas")
if metadatas:
    logger.info("  Metadata:")
    for i, metadata in enumerate(metadatas):
        logger.info(f"    Document {i + 1}: {metadata}")

# Create a ChromaVectorStore instance
vector_store = ChromaVectorStore(
    chroma_collection=chroma_collection,
)

# Create a StorageContext
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load documents from the ChromaDB collection
documents = []

# Get all documents from the collection
if data and "documents" in data:
    for text in data["documents"]:
        if text:  # Only add non-empty documents
            documents.append(Document(text=text))

# Create the index with the loaded documents
if documents:
    index = VectorStoreIndex.from_documents(
        documents=documents,
        storage_context=storage_context,
    )
    logger.info(f"Created index with {len(documents)} documents")
else:
    logger.warning("No documents found in the collection. Index not created.")
    index = None

# define LLM
llm = Ollama(
    request_timeout=300.0,
    model="mistral",
    base_url="http://middleware:8001",  # URL du middleware
    api_key="not-needed",  # Nécessaire pour la compatibilité avec l'API OpenAI
)


@cl.on_message
async def main(message: cl.Message):
    # Récupérer le contenu du message
    content = message.content
    logger.info(f"Received message: {content}")

    # Create empty message
    msg = cl.Message(content="")
    await msg.send()

    try:
        if not index:
            msg.content = "Error: Index not loaded. Please check the configuration."
            await msg.update()
            return

        logger.info("Using query engine with context...")

        # Log index details before query
        logger.info(f"Index details - Number of documents: {len(index.docstore.docs)}")

        query_engine = index.as_query_engine(
            llm=llm,
            streaming=False,
            response_mode="tree_summarize",
            verbose=True,
        )

        logger.info("Sending query to query engine...")
        response = query_engine.query(content)
        logger.info(f"Raw response from query engine: {response}")
        logger.info(f"Response type: {type(response)}")

        # Process the response
        if response and str(response).strip():
            logger.info("Setting response content...")
            msg.content = str(response)
            await msg.update()
        else:
            logger.warning("Empty or invalid response received from query engine")
            msg.content = (
                "Empty response from query engine. Please check the configuration."
            )
            await msg.update()

    except Exception as e:
        logger.error(f"Error during query engine request: {e}")
        msg.content = f"Error: {str(e)}"
        await msg.update()
