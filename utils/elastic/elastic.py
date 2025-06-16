from langchain_elasticsearch import ElasticsearchStore
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_elasticsearch import BM25Strategy
from langchain_openai import OpenAIEmbeddings
from elasticsearch import Elasticsearch
import subprocess
import os
from dotenv import load_dotenv
load_dotenv()
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')

# Fingerprint from Elasticsearch
# Colons and uppercase/lowercase don't matter when using
# the 'ssl_assert_fingerprint' parameter
command = "openssl s_client -connect localhost:9200 -servername localhost -showcerts </dev/null 2>/dev/null \
            | openssl x509 -fingerprint -sha256 -noout -in /dev/stdin"
result = subprocess.check_output(command, shell=True, text=True)
#get just the fingerprint from the output by splitting it on = and stripping ending newline
CERT_FINGERPRINT = result.split("=")[1].strip()

client = Elasticsearch(
    "https://localhost:9200",
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

# elastic_vector_search = ElasticsearchStore(
#     #"langchain-demo", embedding=embeddings, es_url="http://localhost:9200"
#     "langchain-demo", es_url="http://localhost:9200"
# )

docs = []
dloader = DirectoryLoader("../../store_location", glob="**/*", use_multithreading=True, loader_cls=TextLoader)
for tdoc in dloader.load(): docs.append(tdoc)

# vector_store = ElasticsearchStore.from_documents(
#     docs,
#     es_url="http://localhost:9200",
#     es_user="elastic",
#     es_password="123456",
#     index_name="langchain-test",
#     embedding=embeddings,
# )

#uuids = [str(uuid4()) for _ in range(len(documents))]

elastic_vector_search.add_documents(documents=docs)