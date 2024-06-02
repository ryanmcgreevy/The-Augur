from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import getpass
import os
from os import walk
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain.storage._lc_store import create_kv_docstore
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage.file_system import LocalFileStore

#from langchain_community.embeddings import OllamaEmbeddings
#for offline llm
#embeddings = OllamaEmbeddings()

#Uncomment if you want to pass the API key every time. You can also set it directly here.
#For now, we are using the environment variable set by our bash profile
#os.environ["OPENAI_API_KEY"] = getpass.getpass()

def scrape_and_store():
    embeddings=OpenAIEmbeddings()

    loader = WebBaseLoader(["https://sites.google.com/view/mh-guilds/guides-and-stuff/rules-policies", 
                        "https://sites.google.com/view/mh-guilds/welcome",
                        "https://sites.google.com/view/mh-guilds/guides/trading",
                        "https://sites.google.com/view/mh-guilds/guides/healer-role",
                        "https://sites.google.com/view/mh-guilds/guides/tank-role",
                        "https://sites.google.com/view/mh-guilds/guides/dps-role",
                        "https://sites.google.com/view/mh-guilds/raffle",
                        "https://sites.google.com/view/mh-guilds/trial-notes/aetherian-archive",
                        "https://sites.google.com/view/mh-guilds/guides/scribing"])


    docs = loader.load()

    for (dirpath, dirnames, filenames) in walk('context_files/'):
        dloader = DirectoryLoader(dirpath, glob="**/*.txt", loader_cls=TextLoader, use_multithreading=True)
        for tdoc in dloader.load(): docs.append(tdoc)
    for (dirpath, dirnames, filenames) in walk('context_files/md/'):  
        dloader = DirectoryLoader(dirpath, glob="**/*.md", use_multithreading=True)
        for tdoc in dloader.load(): docs.append(tdoc)
    print(len(docs))
    #chunk_size = 1000
    #chunk_overlap = 200
    #text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    #splits = text_splitter.split_documents(docs)
    #vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory="./chroma_db")

    fs = LocalFileStore("./store_location")
    store = create_kv_docstore(fs)
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

    vectorstore = Chroma(collection_name="split_parents", embedding_function=embeddings, persist_directory="./db")
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        #parent_splitter=parent_splitter,
    )
    retriever.add_documents(docs, ids=None)

scrape_and_store()