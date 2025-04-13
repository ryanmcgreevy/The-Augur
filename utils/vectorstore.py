from langchain_chroma import Chroma
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from os import walk
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain.storage._lc_store import create_kv_docstore
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage.file_system import LocalFileStore
import argparse
import os
from dotenv import load_dotenv
load_dotenv()
CHROMA_URL = os.getenv('CHROMA_URL')
CHROMA_PORT = os.getenv('CHROMA_PORT')

#from langchain_community.embeddings import OllamaEmbeddings
#for offline llm
#embeddings = OllamaEmbeddings()

#Uncomment if you want to pass the API key every time. You can also set it directly here.
#For now, we are using the environment variable set by our bash profile
#os.environ["OPENAI_API_KEY"] = getpass.getpass()

def scrape_and_store(name,mode):
    embeddings=OpenAIEmbeddings()

    #local embeddings
    #from langchain_ollama import OllamaEmbeddings
    #embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    docs = []

    if mode == 'dir':
        dloader = DirectoryLoader(name, glob="**/*", use_multithreading=True)
        for tdoc in dloader.load(): docs.append(tdoc)
    elif mode == 'file':
        loader = TextLoader(name)

        docs = loader.load()
    print(len(docs))
    
    fs = LocalFileStore("./store_location")
    store = create_kv_docstore(fs)
    #not splitting parents right now
    #parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
    
    #local chroma for testing
    #vectorstore = Chroma(collection_name="split_children", embedding_function=embeddings, persist_directory="./db")
    
    #chroma client for production
    chroma_client = chromadb.HttpClient(
        host=CHROMA_URL, 
        port=CHROMA_PORT
    )

    vectorstore = Chroma(
        collection_name="split_children", 
        embedding_function=embeddings, 
        client=chroma_client
    )

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        #parent_splitter=parent_splitter,
    )

    def batch_process(documents_arr, batch_size, process_function):
        for i in range(0, len(documents_arr), batch_size):
            batch = documents_arr[i:i + batch_size]
            process_function(batch)

    def add_to_chroma_database(batch):
        retriever.add_documents(documents=batch)

    # #limit is 41666, but because we are passing the child splitter to ParentDocumentRetriever,
    # #and not just splitting the docs and feeding them in ourselves, we need to make this batch size
    # #relatively small to make sure we don't exceed the limit as the retriever is splitting the doc input
    batch_size = 50

    batch_process(docs, batch_size, add_to_chroma_database)

    retriever.add_documents(docs, ids=None)

parser = argparse.ArgumentParser("vectorstore")
parser.add_argument("path", help="Path of directory (for dir mode) or filename (for file mode).", type=str)
parser.add_argument("mode", help="dir | file to determine whether to load all files in a directory or add a single file to the database.", type=str, choices=['dir', 'file'], )
args = parser.parse_args()
scrape_and_store(name=args.path,mode=args.mode)
