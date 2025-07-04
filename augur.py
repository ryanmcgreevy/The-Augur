from langchain_chroma import Chroma
import chromadb
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage._lc_store import create_kv_docstore
from langchain.storage.file_system import LocalFileStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_elasticsearch import ElasticsearchStore
from elasticsearch import Elasticsearch
from langchain_elasticsearch import BM25Strategy
import subprocess
import os
from dotenv import load_dotenv
load_dotenv()
CHROMA_URL = os.getenv('CHROMA_URL')
ELASTIC_URL = os.getenv('ELASTIC_URL')
CHROMA_PORT = os.getenv('CHROMA_PORT')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
class Augur:

    def __init__(self) -> None:
        
        #for offline llm
        #from langchain_ollama.llms import OllamaLLM
        #from langchain_community.embeddings import OllamaEmbeddings
        #for offline llm
        #self.llm = OllamaLLM(model="llama3.2")
        #embeddings = OllamaEmbeddings()

        #Uncomment if you want to pass the API key every time. You can also set it directly here.
        #For now, we are using the environment variable set by our bash profile
        #os.environ["OPENAI_API_KEY"] = getpass.getpass()

        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.embeddings=OpenAIEmbeddings()

        # fs = LocalFileStore("./store_location")
        # store = create_kv_docstore(fs)

        # docs = []
        # dloader = DirectoryLoader("./store_location", glob="**/*", use_multithreading=True, loader_cls=TextLoader)
        # for tdoc in dloader.load(): docs.append(tdoc)
        # bmretriever = BM25Retriever.from_documents(docs)
  
        # #not using parent splitters for now
        # #parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
        # child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

        # #local chroma for testing
        # #self.vectorstore = Chroma(collection_name="split_children", embedding_function=self.embeddings, persist_directory="./db")
        # #chroma client for production
        # chroma_client = chromadb.HttpClient(
        #     host=CHROMA_URL, 
        #     port=CHROMA_PORT
        # )

        # self.vectorstore = Chroma(
        #     collection_name="split_children", 
        #     embedding_function=self.embeddings, 
        #     client=chroma_client
        # )

        # self.retriever = ParentDocumentRetriever(
        #     vectorstore=self.vectorstore,
        #     docstore=store,
        #     child_splitter=child_splitter,
	    #     search_kwargs= {"k":6},
        # )

        # Fingerprint from Elasticsearch
        # Colons and uppercase/lowercase don't matter when using
        # the 'ssl_assert_fingerprint' parameter
        command = "openssl s_client -connect "+ELASTIC_URL+":9200 -servername localhost -showcerts </dev/null 2>/dev/null \
                  | openssl x509 -fingerprint -sha256 -noout -in /dev/stdin"
        result = subprocess.check_output(command, shell=True, text=True)
        #get just the fingerprint from the output by splitting it on = and stripping ending newline
        CERT_FINGERPRINT = result.split("=")[1].strip()

        client = Elasticsearch(
            "https://"+ELASTIC_URL+":9200",
            ssl_assert_fingerprint=CERT_FINGERPRINT,
            basic_auth=("elastic", ELASTIC_PASSWORD)
        )

        # Successful response!
        client.info()
        # {'name': 'instance-0000000000', 'cluster_name': ...}

        elastic_vector_search = ElasticsearchStore(
            #es_url="http://localhost:9200",
            es_connection=client,
            index_name="langchain_index",
            strategy=BM25Strategy(),
            #  embedding=embeddings,
            #  es_user="elastic",
            #  es_password="123456",
        )
        
        retriever = elastic_vector_search.as_retriever()

        #local chroma for testing
        #self.oldvectorstore = Chroma(persist_directory="./db", embedding_function=self.embeddings)
        #chroma client for production
        # can't use vectorstore we made for parent doc retriever because the embedded text isnt stored, it points to 
        # the docs. Not sure this works without making a separate "normal" vectorstore
        # self.oldvectorstore = Chroma(
        #     client=chroma_client, 
        #     embedding_function=self.embeddings
        # )
        # self.otherretriever = self.oldvectorstore.as_retriever(
        #     search_type="mmr", 
        #     search_kwargs={"lambda_mult":.5, "k":6}
        # )

        #initialize the ensemble retriever
        # self.ensemble_retriever = EnsembleRetriever(
        #      retrievers=[self.retriever, bmretriever], 
        #      weights=[0.5, 0.5]
        #  )

        self.prompt = ChatPromptTemplate.from_template("""Answer as if you are a friendly member of the guild.\
            Answer with as much specific detail as possible. \
            Answer the following question based only on the provided context. \
            Use the specific wording of the context as much as possible:

        <context>
        {context}
        </context>

        Question: {input}""")

        document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
    async def invoke_llm(self, user_input):
        print("invoking llm...")
        response = await self.retrieval_chain.ainvoke({"input": user_input})
        #uncomment for debugging the context that is being retrieved and sent to the llm
        print(response.get('context'))
        return response

  


