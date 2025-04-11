import os

import chromadb
from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

# Définir les chemins
# Répertoire de travail
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Créer le répertoire de la base de données s'il n'existe pas
os.makedirs("chroma_db", exist_ok=True)

# Initialiser la base de données ChromaDB
client = chromadb.PersistentClient(path="chroma_db")

# Créer ou obtenir la collection
chroma_collection = client.get_or_create_collection(name="genai")

# Initialiser l'embedding model de Hugging Face
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# Créer le vector store avec ChromaDB
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Charger les documents du répertoire
documents = SimpleDirectoryReader("data").load_data()

# Traiter chaque document et vérifier s'il existe déjà
for doc in documents:
    doc_id = os.path.basename(doc.metadata["file_path"])
    doc_content = doc.text

    # Vérifier si le document existe déjà (par son ID)
    existing_ids = chroma_collection.get(ids=[doc_id])["ids"]

    if existing_ids and doc_id in existing_ids:
        # Mettre à jour le document existant
        chroma_collection.update(
            ids=[doc_id], documents=[doc_content], metadatas=[doc.metadata]
        )
        print(f"Document mis à jour: {doc_id}")
    else:
        # Ajouter un nouveau document
        chroma_collection.add(
            ids=[doc_id], documents=[doc_content], metadatas=[doc.metadata]
        )
        print(f"Document ajouté: {doc_id}")

print("\n=== Fin du traitement ===")
print(
    f"Tous les documents ont été chargés dans la collection '{chroma_collection.name}'."
)

# Afficher les informations sur la base ChromaDB
print("\n=== Informations sur la base ChromaDB ===")
collection_info = chroma_collection.get(
    include=["metadatas", "documents", "embeddings"]
)

# Afficher les informations sur la collection
print(f"Collection: {chroma_collection.name}")
print(f"Nombre de documents: {len(collection_info['ids'])}")
print(
    f"Longueur totale des documents: {sum(len(doc) for doc in collection_info['documents'])}"
)
print(f"Nombre d'embeddings: {len(collection_info['embeddings'][0])}")

# Pour chaque document, afficher les métadonnées
print("\n=== Informations sur les documents ===")
print("\n=== Informations sur les documents ===")
for i, (doc_id, metadata) in enumerate(
    zip(collection_info["ids"], collection_info["metadatas"])
):
    print(f"\n---------- Document {i + 1}/{len(collection_info['ids'])} ----------")
    print(f"ID: {doc_id}")
    print("Métadonnées:")
    for key, value in metadata.items():
        print(f"  - {key}: {value}")
    print("-" * 40)  # Ligne séparatrice
