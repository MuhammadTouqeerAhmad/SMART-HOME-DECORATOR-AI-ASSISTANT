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


# --------------------------------------------------
# Clients
# --------------------------------------------------

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)

chroma_client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)


# --------------------------------------------------
# Document Loading
# --------------------------------------------------

def load_documents():
    """
    Load all knowledge files from the design knowledge
    directory recursively.
    """

    documents = []

    for file_path in KNOWLEDGE_DIR.rglob("*.txt"):

        text = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not text:
            continue

        relative_path = file_path.relative_to(
            KNOWLEDGE_DIR
        )

        parts = relative_path.parts

        category = (
            parts[0]
            if len(parts) > 1
            else "general"
        )

        documents.append({
            "filename": file_path.name,
            "path": str(relative_path),
            "category": category,
            "text": text
        })

    return documents


# --------------------------------------------------
# Text Chunking
# --------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
):
    """
    Split long documents into overlapping chunks.

    Overlap helps preserve context between chunks.
    """

    if not text:
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
    """
    Generate an embedding using Gemini.
    """

    result = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )

    return result.embeddings[0].values


# --------------------------------------------------
# Build Knowledge Base
# --------------------------------------------------

def build_knowledge_base():
    """
    Read all knowledge documents, split them into
    chunks, generate embeddings and store them
    inside Chroma.
    """

    documents = load_documents()

    ids = []
    embeddings = []
    texts = []
    metadatas = []

    counter = 0

    for document in documents:

        chunks = chunk_text(
            document["text"]
        )

        for chunk_index, chunk in enumerate(chunks):

            embedding = create_embedding(
                chunk
            )

            ids.append(
                f"{document['path']}-{chunk_index}"
            )

            embeddings.append(
                embedding
            )

            texts.append(
                chunk
            )

            metadatas.append({
                "source": document["filename"],
                "path": document["path"],
                "category": document["category"],
                "chunk_index": chunk_index
            })

            counter += 1

    if not ids:
        return 0

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

    return counter


# --------------------------------------------------
# Retrieval
# --------------------------------------------------

def retrieve_knowledge(
    query: str,
    top_k: int = 6
):
    """
    Retrieve the most relevant knowledge chunks.
    """

    if not query.strip():
        return []

    query_embedding = create_embedding(
        query
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    retrieved = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        retrieved.append({
            "content": document,
            "source": metadata.get(
                "source",
                "unknown"
            ),
            "path": metadata.get(
                "path",
                ""
            ),
            "category": metadata.get(
                "category",
                "general"
            ),
            "distance": distance
        })

    return retrieved