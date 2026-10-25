# from pathlib import Path

# from chromadb import PersistentClient


# KNOWLEDGE_DIR = Path(
#     "data/design_knowledge"
# )

# CHROMA_DIR = "chroma_db"


# client = PersistentClient(
#     path=CHROMA_DIR
# )

# from pathlib import Path

# import chromadb
# from google import genai

# from src.config import GEMINI_API_KEY


# # --------------------------------------------------
# # Configuration
# # --------------------------------------------------

# KNOWLEDGE_DIR = Path(
#     "data/design_knowledge"
# )

# CHROMA_DIR = "chroma_db"

# COLLECTION_NAME = "design_knowledge"

# EMBEDDING_MODEL = "gemini-embedding-2"


# # --------------------------------------------------
# # Clients
# # --------------------------------------------------

# gemini_client = genai.Client(
#     api_key=GEMINI_API_KEY
# )


# chroma_client = chromadb.PersistentClient(
#     path=CHROMA_DIR
# )


# collection = chroma_client.get_or_create_collection(
#     name=COLLECTION_NAME
# )

# def load_documents():

#     documents = []

#     for file_path in KNOWLEDGE_DIR.glob("*.txt"):

#         text = file_path.read_text(
#             encoding="utf-8"
#         )

#         documents.append({

#             "filename": file_path.name,

#             "text": text
#         })

#     return documents

# def chunk_text(
#     text: str,
#     chunk_size: int = 800,
#     overlap: int = 100
# ):

#     chunks = []

#     start = 0

#     while start < len(text):

#         end = start + chunk_size

#         chunk = text[start:end].strip()

#         if chunk:

#             chunks.append(chunk)

#         start += chunk_size - overlap

#     return chunks

# def create_embedding(
#     text: str
# ):

#     result = gemini_client.models.embed_content(

#         model=EMBEDDING_MODEL,

#         contents=text
#     )

#     return result.embeddings[0].values

# def build_knowledge_base():

#     documents = load_documents()

#     ids = []

#     embeddings = []

#     texts = []

#     metadatas = []


#     counter = 0


#     for document in documents:

#         chunks = chunk_text(
#             document["text"]
#         )


#         for chunk in chunks:

#             embedding = create_embedding(
#                 chunk
#             )


#             ids.append(
#                 f"chunk-{counter}"
#             )

#             embeddings.append(
#                 embedding
#             )

#             texts.append(
#                 chunk
#             )

#             metadatas.append({

#                 "source":
#                     document["filename"]
#             })


#             counter += 1


#     if ids:

#         collection.upsert(

#             ids=ids,

#             embeddings=embeddings,

#             documents=texts,

#             metadatas=metadatas
#         )


#     return len(ids)

# def retrieve_knowledge(
#     query: str,
#     top_k: int = 4
# ):

#     query_embedding = create_embedding(
#         query
#     )


#     results = collection.query(

#         query_embeddings=[
#             query_embedding
#         ],

#         n_results=top_k
#     )


#     documents = results.get(
#         "documents",
#         [[]]
#     )[0]


#     metadatas = results.get(
#         "metadatas",
#         [[]]
#     )[0]


#     retrieved = []


#     for document, metadata in zip(
#         documents,
#         metadatas
#     ):

#         retrieved.append({

#             "content": document,

#             "source":
#                 metadata["source"]
#         })


#     return retrieved

# from pathlib import Path

# import chromadb
# from google import genai

# from src.config import GEMINI_API_KEY


# # --------------------------------------------------
# # Configuration
# # --------------------------------------------------

# KNOWLEDGE_DIR = Path("data/design_knowledge")
# CHROMA_DIR = "chroma_db"

# COLLECTION_NAME = "design_knowledge"

# EMBEDDING_MODEL = "gemini-embedding-2"


# # --------------------------------------------------
# # Clients
# # --------------------------------------------------

# gemini_client = genai.Client(
#     api_key=GEMINI_API_KEY
# )

# chroma_client = chromadb.PersistentClient(
#     path=CHROMA_DIR
# )

# collection = chroma_client.get_or_create_collection(
#     name=COLLECTION_NAME
# )


# # --------------------------------------------------
# # Document Loading
# # --------------------------------------------------

# def load_documents():
#     """
#     Load all knowledge files from the design knowledge
#     directory recursively.
#     """

#     documents = []

#     for file_path in KNOWLEDGE_DIR.rglob("*.txt"):

#         text = file_path.read_text(
#             encoding="utf-8"
#         ).strip()

#         if not text:
#             continue

#         relative_path = file_path.relative_to(
#             KNOWLEDGE_DIR
#         )

#         parts = relative_path.parts

#         category = (
#             parts[0]
#             if len(parts) > 1
#             else "general"
#         )

#         documents.append({
#             "filename": file_path.name,
#             "path": str(relative_path),
#             "category": category,
#             "text": text
#         })

#     return documents


# # --------------------------------------------------
# # Text Chunking
# # --------------------------------------------------

# def chunk_text(
#     text: str,
#     chunk_size: int = 1000,
#     overlap: int = 150
# ):
#     """
#     Split long documents into overlapping chunks.

#     Overlap helps preserve context between chunks.
#     """

#     if not text:
#         return []

#     chunks = []

#     start = 0

#     while start < len(text):

#         end = start + chunk_size

#         chunk = text[start:end].strip()

#         if chunk:
#             chunks.append(chunk)

#         if end >= len(text):
#             break

#         start += chunk_size - overlap

#     return chunks


# # --------------------------------------------------
# # Embeddings
# # --------------------------------------------------

# def create_embedding(text: str):
#     """
#     Generate an embedding using Gemini.
#     """

#     result = gemini_client.models.embed_content(
#         model=EMBEDDING_MODEL,
#         contents=text
#     )

#     return result.embeddings[0].values


# # --------------------------------------------------
# # Build Knowledge Base
# # --------------------------------------------------

# def build_knowledge_base():
#     """
#     Read all knowledge documents, split them into
#     chunks, generate embeddings and store them
#     inside Chroma.
#     """

#     documents = load_documents()

#     ids = []
#     embeddings = []
#     texts = []
#     metadatas = []

#     counter = 0

#     for document in documents:

#         chunks = chunk_text(
#             document["text"]
#         )

#         for chunk_index, chunk in enumerate(chunks):

#             embedding = create_embedding(
#                 chunk
#             )

#             ids.append(
#                 f"{document['path']}-{chunk_index}"
#             )

#             embeddings.append(
#                 embedding
#             )

#             texts.append(
#                 chunk
#             )

#             metadatas.append({
#                 "source": document["filename"],
#                 "path": document["path"],
#                 "category": document["category"],
#                 "chunk_index": chunk_index
#             })

#             counter += 1

#     if not ids:
#         return 0

#     collection.upsert(
#         ids=ids,
#         embeddings=embeddings,
#         documents=texts,
#         metadatas=metadatas
#     )

#     return counter


# # --------------------------------------------------
# # Retrieval
# # --------------------------------------------------

# def retrieve_knowledge(
#     query: str,
#     top_k: int = 6
# ):
#     """
#     Retrieve the most relevant knowledge chunks.
#     """

#     if not query.strip():
#         return []

#     query_embedding = create_embedding(
#         query
#     )

#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=top_k
#     )

#     documents = results.get(
#         "documents",
#         [[]]
#     )[0]

#     metadatas = results.get(
#         "metadatas",
#         [[]]
#     )[0]

#     distances = results.get(
#         "distances",
#         [[]]
#     )[0]

#     retrieved = []

#     for document, metadata, distance in zip(
#         documents,
#         metadatas,
#         distances
#     ):

#         retrieved.append({
#             "content": document,
#             "source": metadata.get(
#                 "source",
#                 "unknown"
#             ),
#             "path": metadata.get(
#                 "path",
#                 ""
#             ),
#             "category": metadata.get(
#                 "category",
#                 "general"
#             ),
#             "distance": distance
#         })

#     return retrieved


from pathlib import Path

import chromadb
from google import genai

from src.config import GEMINI_API_KEY


# --------------------------------------------------
# Configuration
# --------------------------------------------------

KNOWLEDGE_DIR = Path("data/design_knowledge")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "design_knowledge"
EMBEDDING_MODEL = "gemini-embedding-2"

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)


# --------------------------------------------------
# Document Loading
# --------------------------------------------------

def load_documents():
    """Load non-empty knowledge files recursively."""

    documents = []

    if not KNOWLEDGE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge directory not found: {KNOWLEDGE_DIR}"
        )

    for file_path in sorted(KNOWLEDGE_DIR.rglob("*.txt")):
        content = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            continue

        relative_path = file_path.relative_to(
            KNOWLEDGE_DIR
        )

        category = (
            relative_path.parts[0]
            if len(relative_path.parts) > 1
            else "general"
        )

        documents.append({
            "filename": file_path.name,
            "path": relative_path.as_posix(),
            "category": category,
            "text": content,
        })

    return documents


# --------------------------------------------------
# Text Chunking
# --------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150,
):
    """Split text into overlapping character-based chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and smaller than chunk_size"
        )

    if not text or not text.strip():
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start += chunk_size - overlap

    return chunks


# --------------------------------------------------
# Embeddings
# --------------------------------------------------

def create_embedding(text: str):
    """Generate a Gemini embedding for a text string."""

    result = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )

    if not result.embeddings:
        raise RuntimeError("Gemini returned no embeddings")

    return result.embeddings[0].values


# --------------------------------------------------
# Build / Synchronize Knowledge Base
# --------------------------------------------------

def build_knowledge_base():
    """
    Synchronize Chroma with current knowledge files.

    - Adds new chunks.
    - Updates changed chunks.
    - Updates metadata when only metadata changes.
    - Removes obsolete chunk IDs.
    - Avoids re-embedding unchanged text.
    """

    documents = load_documents()

    # Do not erase an existing knowledge base if files
    # are missing or the directory contains no usable text.
    if not documents:
        raise ValueError(
            f"No non-empty .txt files found in {KNOWLEDGE_DIR}. "
            "Existing Chroma data has been left unchanged."
        )

    desired_records = {}

    for document in documents:
        chunks = chunk_text(document["text"])

        for chunk_index, chunk in enumerate(chunks):
            chunk_id = (
                f"{document['path']}-{chunk_index}"
            )

            desired_records[chunk_id] = {
                "text": chunk,
                "metadata": {
                    "source": document["filename"],
                    "path": document["path"],
                    "category": document["category"],
                    "chunk_index": chunk_index,
                },
            }

    if not desired_records:
        raise ValueError(
            "No chunks were generated. Existing Chroma data "
            "has been left unchanged."
        )

    existing = collection.get(
        include=["documents", "metadatas"]
    )

    existing_records = {}

    for index, chunk_id in enumerate(existing["ids"]):
        existing_records[chunk_id] = {
            "text": existing["documents"][index],
            "metadata": existing["metadatas"][index] or {},
        }

    ids_to_upsert = []
    texts_to_upsert = []
    embeddings_to_upsert = []
    metadata_to_upsert = []

    metadata_update_ids = []
    metadata_updates = []

    # Add new chunks or update changed content.
    for chunk_id, record in desired_records.items():
        old_record = existing_records.get(chunk_id)

        if old_record and old_record["text"] == record["text"]:
            # Content is unchanged, so reuse its existing embedding.
            if old_record["metadata"] != record["metadata"]:
                metadata_update_ids.append(chunk_id)
                metadata_updates.append(record["metadata"])

            continue

        # Embed only new or changed content.
        embedding = create_embedding(record["text"])

        ids_to_upsert.append(chunk_id)
        texts_to_upsert.append(record["text"])
        embeddings_to_upsert.append(embedding)
        metadata_to_upsert.append(record["metadata"])

    # Save new or changed chunks.
    if ids_to_upsert:
        collection.upsert(
            ids=ids_to_upsert,
            embeddings=embeddings_to_upsert,
            documents=texts_to_upsert,
            metadatas=metadata_to_upsert,
        )

    # Update metadata without regenerating embeddings.
    if metadata_update_ids:
        collection.update(
            ids=metadata_update_ids,
            metadatas=metadata_updates,
        )

    # Remove records whose files/chunks no longer exist.
    desired_ids = set(desired_records)
    stale_ids = [
        chunk_id
        for chunk_id in existing["ids"]
        if chunk_id not in desired_ids
    ]

    if stale_ids:
        collection.delete(ids=stale_ids)

    print(
        f"RAG sync: {len(ids_to_upsert)} new/changed chunks, "
        f"{len(metadata_update_ids)} metadata updates, "
        f"{len(stale_ids)} obsolete chunks removed."
    )

    return len(desired_records)


# --------------------------------------------------
# Retrieval
# --------------------------------------------------

def retrieve_knowledge(
    query: str,
    top_k: int = 6,
):
    """Retrieve relevant, non-duplicate knowledge chunks."""

    if not query or not query.strip():
        return []

    if top_k <= 0:
        return []

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    query_embedding = create_embedding(query)

    # Fetch extra candidates because some may be duplicates.
    candidate_count = min(total_chunks, top_k * 3)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=candidate_count,
        include=["documents", "metadatas", "distances"],
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved = []
    seen_content = set()

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        # Ignore exact duplicates after normalizing whitespace
        # and capitalization.
        normalized = " ".join(document.casefold().split())

        if normalized in seen_content:
            continue

        seen_content.add(normalized)

        metadata = metadata or {}

        retrieved.append({
            "content": document,
            "source": metadata.get("source", "unknown"),
            "path": metadata.get("path", ""),
            "category": metadata.get("category", "general"),
            "distance": distance,
        })

        if len(retrieved) >= top_k:
            break

    return retrieved
