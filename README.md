This is a simple RAG implementation featuring the Langchain framework that integrates a MongoDB database to store documents and conversations and a FastAPI server that exposes some endpoints which can be recalled from a frontend application. Everything is enclosed in a Docker container.

In order for this to work, it is assumed that a MongoDB endpoint is accessible in the localhost. 
Moreover, the application was developed by leveraging OpenAPI endpoints, exposed from a machine where an instance of Llama3 was deployed.

With this said, you need to setup a `config.ini` file in `src/configs` in the following way:

```ini
[MONGODB]
HOST = localhost
PORT = 27017
DOCS_DB = papers
DOCS_COLLECTION = papers_collection_proj
HISTORY_DB = conversation_history
HISTORY_COLLECTION = history_collection_proj


[MODEL]
API_BASE = *insert OpenAPI endpoint here*
```

Then just `docker build` the image and run it assuring that it is in the same network of the MongoDB instance.

Things I will do when I will have the time:
- Generalise the configuration in order to implement external API calls such as OpenAI / Gemini.
- Integrate a simple frontend using Vue.js