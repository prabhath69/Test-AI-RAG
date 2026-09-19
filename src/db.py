import os
from langchain_postgres import PGVector
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = f"postgresql+psycopg://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}"

collection_name = "aster_row_knowledge"

def get_embeddings():
    return AzureOpenAIEmbeddings(
        azure_deployment=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
        openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_key=os.environ.get("AZURE_OPENAI_API_KEY")
    )

def get_vector_store():
    embeddings = get_embeddings()
    return PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=CONNECTION_STRING,
        use_jsonb=True,
    )
