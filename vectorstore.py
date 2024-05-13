from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
import getpass
import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
os.environ["OPENAI_API_KEY"] = getpass.getpass()

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
embeddings=OpenAIEmbeddings()

loader = WebBaseLoader("https://sites.google.com/view/mh-guilds/guides-and-stuff/rules-policies")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory="./chroma_db")
