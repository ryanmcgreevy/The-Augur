import chromadb
import os
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from os import walk
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain.storage._lc_store import create_kv_docstore
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage.file_system import LocalFileStore
import hashlib
# from dotenv import load_dotenv
# load_dotenv()
# CHROMA_URL = os.getenv('CHROMA_URL')
# CHROMA_PORT = os.getenv('CHROMA_PORT')

# chroma_client = chromadb.HttpClient(
#     host=CHROMA_URL, 
#     port=CHROMA_PORT
# )

client = chromadb.PersistentClient(path='../db_test')

embeddings=OpenAIEmbeddings()

#local embeddings
#from langchain_ollama import OllamaEmbeddings
#embeddings = OllamaEmbeddings(model="mxbai-embed-large")

docs = []
name = "test.txt"
loader = TextLoader(name)
docs = loader.load()
id = str(hashlib.sha256(name.encode()).hexdigest())
ids = [id]
docs[0].metadata = {"id":id, "source":name}
#not splitting parents right now
#parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
#child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

#local chroma for testing
#vectorstore = Chroma(collection_name="split_children", embedding_function=embeddings, persist_directory="../db_test")


vectorstore = Chroma(
    collection_name="split_children", 
    embedding_function=embeddings, 
    client=client
)

retriever = vectorstore.as_retriever()

retriever.add_documents(documents=docs,ids=ids)


for collection_name in client.list_collections():
    
    collection = client.get_collection(collection_name)
    data = collection.get()

    ids = data['ids']
    embeddings = data["embeddings"]
    metadata = data["metadatas"]
    documents = data["documents"]

print(ids)
print(metadata)
print(documents)