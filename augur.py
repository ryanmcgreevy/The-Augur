from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage._lc_store import create_kv_docstore
from langchain.storage.file_system import LocalFileStore
from langchain.storage import InMemoryStore
from langchain.storage import InMemoryByteStore
import getpass
import os
from os import walk
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.document_loaders import TextLoader
import urllib.request
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers import EnsembleRetriever
import discord


class Augur:

    def __init__(self) -> None:
        
        #for offline llm
        #from langchain_community.llms import Ollama
        #from langchain_community.embeddings import OllamaEmbeddings
        #for offline llm
        #llm = Ollama(model="llama3")
        #embeddings = OllamaEmbeddings()

        #Uncomment if you want to pass the API key every time. You can also set it directly here.
        #For now, we are using the environment variable set by our bash profile
        #os.environ["OPENAI_API_KEY"] = getpass.getpass()

        #llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
        self.llm = ChatOpenAI(model="gpt-4o")
        self.embeddings=OpenAIEmbeddings()

        child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

        #self.vectorstore = Chroma(persist_directory="chroma_db", embedding_function=self.embeddings)
        #self.retriever = self.vectorstore.as_retriever(search_type="mmr", search_kwargs={"lambda_mult":0.5, "k":6})
        fs = LocalFileStore("./store_location")
        store = create_kv_docstore(fs)
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

        self.vectorstore = Chroma(collection_name="split_parents", embedding_function=self.embeddings, persist_directory="./db")
        self.retriever = ParentDocumentRetriever(
        vectorstore=self.vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        #search_type="mmr", 
        #search_kwargs= {"lambda_mult":.5, "k":6},
        #parent_splitter=parent_splitter,
        )

        self.oldvectorstore = Chroma(persist_directory="chroma_db", embedding_function=self.embeddings)
        self.otherretriever = self.oldvectorstore.as_retriever(search_type="mmr", search_kwargs={"lambda_mult":.5, "k":6})

        # initialize the ensemble retriever
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.retriever, self.otherretriever], weights=[0.5, 0.5]
        )

        #store = InMemoryStore()
        # self.retriever = ParentDocumentRetriever(
        #     vectorstore=self.vectorstore,
        #     docstore=store,
        #     child_splitter=child_splitter,
        # )
        self.prompt = ChatPromptTemplate.from_template("""Answer as if you are a friendly member of the guild. Answer with as much specific detail as possible. Answer the following question based only on the provided context and use the specific wording of the context as much as possible:

        <context>
        {context}
        </context>

        Question: {input}""")

        document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.retrieval_chain = create_retrieval_chain(self.ensemble_retriever, document_chain)
        

    # def scrape_and_store(self):
    #     loader = WebBaseLoader(["https://sites.google.com/view/mh-guilds/guides-and-stuff/rules-policies", 
    #                         "https://sites.google.com/view/mh-guilds/welcome",
    #                         "https://sites.google.com/view/mh-guilds/guides/trading",
    #                         "https://sites.google.com/view/mh-guilds/guides/healer-role",
    #                         "https://sites.google.com/view/mh-guilds/guides/tank-role",
    #                         "https://sites.google.com/view/mh-guilds/guides/dps-role",
    #                         "https://sites.google.com/view/mh-guilds/raffle",
    #                         "https://sites.google.com/view/mh-guilds/trial-notes/aetherian-archive",
    #                         "https://sites.google.com/view/mh-guilds/guides/scribing"])


    #     docs = loader.load()

    #     for (dirpath, dirnames, filenames) in walk('context_files/'):
    #        dloader = DirectoryLoader(dirpath, glob="**/*.txt", loader_cls=TextLoader)
    #        for tdoc in dloader.load(): docs.append(tdoc)
    #     for (dirpath, dirnames, filenames) in walk('context_files/md/'):  
    #         dloader = DirectoryLoader(dirpath, glob="**/*.md")
    #         for tdoc in dloader.load(): docs.append(tdoc)

    #     print(len(docs))
    #   #  doc_len = 0
    #   #  for doc in docs: doc_len += len(doc.page_content)
    #  #   chunk_size = (doc_len/len(docs))/10
    #   #  chunk_overlap = chunk_size/5
    #     chunk_size = 1000
    #     chunk_overlap = 200
    #     text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    #     splits = text_splitter.split_documents(docs)
    #     self.vectorstore = Chroma.from_documents(documents=splits, embedding=self.embeddings, persist_directory="./chroma_db")
    #     self.retriever = self.vectorstore.as_retriever(search_type="mmr", search_kwargs={"lambda_mult":0.75, "k":5})
    #     document_chain = create_stuff_documents_chain(self.llm, self.prompt)
    #     self.retrieval_chain = create_retrieval_chain(self.retriever, document_chain)

    #This function returns a generator, using a generator comprehension. 
    #The generator returns the string sliced, from 0 + a multiple of the length of the chunks, to the length of the chunks + a multiple of the length of the chunks.
    #You can iterate over the generator like a list, tuple or string - for i in chunkstring(s,n): , or convert it into a list (for instance) with list(generator). 
    #Generators are more memory efficient than lists because they generator their elements as they are needed, not all at once, however they lack certain features like indexing.
    def chunkstring(self, string, length):
        return (string[0+i:length+i] for i in range(0, len(string), length))

    async def invoke_llm(self, user_input, interaction: discord.Interaction):
        print("invoking llm...")
    #await interaction.response.send_message(response)
    #invoking the llm takes too long at this point (beyond the 3 second slash command window)
    #need to defer and use followup instead.
        await interaction.response.defer()
        try:
            response = await self.retrieval_chain.ainvoke({"input": user_input})
            #uncomment for debugging the context that is being retrieved and sent to the llm
            print(response.get('context'))

            answer = response.get('answer')
            for i in self.chunkstring(answer,2000):
                await interaction.followup.send(i)

        except:
            await interaction.followup.send("The Augur isn't feeling well and an error has occured. Please try sending your message again")


