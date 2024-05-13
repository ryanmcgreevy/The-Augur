from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import getpass
import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

#Uncomment if you want to pass the API key every time. You can also set it directly here.
#For now, we are using the environment variable set by our bash profile
#os.environ["OPENAI_API_KEY"] = getpass.getpass()

embeddings=OpenAIEmbeddings()

loader = WebBaseLoader(["https://sites.google.com/view/mh-guilds/guides-and-stuff/rules-policies", 
                       "https://sites.google.com/view/mh-guilds/welcome",
                       "https://sites.google.com/view/mh-guilds/guides/trading",
                       "https://sites.google.com/view/mh-guilds/guides/healer-stuff",
                       "https://sites.google.com/view/mh-guilds/guides/tank-stuff",
                       "https://sites.google.com/view/mh-guilds/guides/parsing-dps",
                       "https://sites.google.com/view/mh-guilds/raffle"])
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory="./chroma_db")
