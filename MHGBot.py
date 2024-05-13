from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import getpass
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

os.environ["OPENAI_API_KEY"] = getpass.getpass()

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
embeddings=OpenAIEmbeddings()


vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_type="similarity")

prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")

document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

print("invoking llm...")


response = retrieval_chain.invoke({"input": "What are the most useful sets to use for Sanity's Edge? Answer in detail."})
print(response["answer"])
