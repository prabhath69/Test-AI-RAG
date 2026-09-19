import os
import glob
import frontmatter
from langchain_core.documents import Document
from db import get_vector_store
from dotenv import load_dotenv

load_dotenv()

def get_markdown_files():
    kb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge-base"))
    return glob.glob(os.path.join(kb_dir, "*.md"))

def seed():
    print("Loading documents...")
    files = get_markdown_files()
    documents = []
    
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
            
            # The prompt requires: Preserve useful metadata from the document front matter.
            # Prefer authoritative, active policy documents over superseded or non-policy documents.
            metadata = post.metadata
            for k, v in metadata.items():
                if hasattr(v, 'isoformat'):
                    metadata[k] = v.isoformat()
            
            metadata["source"] = os.path.basename(file_path)
            
            # We will include all files, but we should make sure the LLM knows the status.
            # We can prepend the metadata to the page_content to ensure the LLM sees it directly,
            # or rely on retriever metadata. Langchain's retrieve doesn't always show metadata to LLM unless formatted.
            content = f"Document: {metadata['title']}\nStatus: {metadata.get('status', 'unknown')}\n\n{post.content}"
            
            doc = Document(
                page_content=content,
                metadata=metadata
            )
            documents.append(doc)
            print(f"Loaded: {os.path.basename(file_path)} - Status: {metadata.get('status')}")
            
    vector_store = get_vector_store()
    
    print("Clearing old documents in collection...")
    # Langchain PGVector doesn't have a simple drop collection without asyncpg usually, 
    # but we can try to use add_documents which just appends. 
    # For idempotency, we can just drop the tables in a real app, but for this intern test,
    # we can run it once. To be safe, we will just add them. 
    # Or initialize fresh.
    try:
        vector_store.drop_tables()
    except Exception as e:
        print(f"Could not drop tables (might not exist yet): {e}")

    # Recreate store
    vector_store = get_vector_store()
    
    print("Embedding and indexing documents...")
    vector_store.add_documents(documents)
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed()
