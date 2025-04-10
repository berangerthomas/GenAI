import logging
import os

import chainlit as cl
import chromadb
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
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

# Create the database directory if it does not exist
os.makedirs("chroma_db", exist_ok=True)

# Configure LlamaIndex to use HuggingFace embeddings
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="chroma_db")

# Try to get the collection, handle if it doesn't exist
chroma_collection = client.get_or_create_collection(name="genai")

# Create vector store with the new collection
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# Create storage context with the vector store
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load documents from the data folder
data_dir = os.path.join(script_dir, "data")
documents = SimpleDirectoryReader(data_dir).load_data()

# Process each document and check if it already exists
for doc in documents:
    doc_id = os.path.basename(doc.metadata["file_path"])
    doc_content = doc.text

    # Check if the document already exists (by its ID)
    existing_ids = chroma_collection.get(ids=[doc_id])["ids"]

    if existing_ids and doc_id in existing_ids:
        # Update existing document
        chroma_collection.update(
            ids=[doc_id], documents=[doc_content], metadatas=[doc.metadata]
        )
        logger.info(f"Document mis à jour: {doc_id}")
    else:
        # Add a new document
        chroma_collection.add(
            ids=[doc_id], documents=[doc_content], metadatas=[doc.metadata]
        )
        logger.info(f"Document ajouté: {doc_id}")

# Create index from the database
# Initialize ChromaDB client
client2 = chromadb.PersistentClient(path="chroma_db")

# Try to get the collection, handle if it doesn't exist
chroma_collection2 = client.get_or_create_collection(name="genai")

# Create vector store with the new collection
vector_store2 = ChromaVectorStore(chroma_collection=chroma_collection2)

# Create storage context with the vector store
storage_context2 = StorageContext.from_defaults(vector_store=vector_store2)

# Create index from the storage context
index = VectorStoreIndex.from_vector_store(vector_store2)

# Check if the index was loaded successfully
if index is None:
    logger.error("Failed to load the index.")
else:
    logger.info("Index loaded successfully.")

# Afficher les informations sur la base ChromaDB
logger.info("\n=== Informations sur la base ChromaDB ===")
collection_info = chroma_collection.get(
    include=["metadatas", "documents", "embeddings"]
)

# Afficher les informations sur la collection
logger.info(f"Collection: {chroma_collection.name}")
logger.info(f"Nombre de documents: {len(collection_info['ids'])}")
logger.info(
    f"Longueur totale des documents: {sum(len(doc) for doc in collection_info['documents'])}"
)
logger.info(f"Nombre d'embeddings: {len(collection_info['embeddings'][0])}")


# define LLM (TinyLlama or Mistral)
llm = Ollama(
    request_timeout=300.0,
    model="TinyLlama",
    base_url="http://middleware:8001",
    api_key="not-needed",
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

        # Extract response text properly
        response_text = str(response).strip()
        logger.info(f"Extracted response text: '{response_text}'")

        # Process the response
        if response_text:
            logger.info("Setting response content...")
            # Méthode 1: Mettre à jour le message vide existant
            msg.content = response_text
            await msg.update()
            logger.info("Message updated with content")

            # OU Méthode 2: Créer un nouveau message (mais pas les deux)
            # await cl.Message(content=response_text).send()
            # logger.info("New message sent with content")
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
