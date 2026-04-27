# The Augur
AI chatbot using langchain for an ESO guild.

This is mostly a learning project for working with LLM chatbots using the LangChain framework. 
The Augur uses a RAG based system to answer questions about the Elder Scrolls Online video game via
interaction through a Discord bot (using Discord.py framework). The chatbot code is containerized using Docker and deployed using GitHub
actions. ElasticSearch is used to store the knowledge base for RAG, which is used to retrieve context that is passed
along with the prompt to the OpenAI api.

The langchain specific RAG and LLM interaction code can be found in *augur.py*
while *augur_discord.py* contains the Discord specific code. Other bash and python files exist for
retrieving, cleaning, and storing the context data for the RAG knowledge base.
