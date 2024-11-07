from src.utils.format_docs import format_docs
from src.template.template import create_template
from langchain_core.runnables.base import RunnableParallel
from operator import itemgetter
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import (
    # RunnableLambda,
    ConfigurableFieldSpec,
    # RunnablePassthrough,
)
from src.model.chatbot.memoryhistory import InMemoryHistory
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class ChatbotWithHistory:
    def __init__(self, user_id: str, conversation_id: str, retriever, model_openapi_url="https://047c-195-230-200-203.ngrok-free.app/v1"):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.model = ChatOpenAI(
            openai_api_base="https://7af2-195-230-200-203.ngrok-free.app/v1",
            api_key="EMPTY",
            temperature=0
        )
        self.template = create_template()
        self.prompt = ChatPromptTemplate.from_template(self.template)

        self.history = {}
        self.chain_with_history = self.create_chain_with_history(retriever)

    def create_chain(self, retriever):
        chain = (
            RunnableParallel({
                            "context": itemgetter("question") | retriever | format_docs,
                            "question": itemgetter("question"),
                            "history": itemgetter("history")
            })
            |{
                "question": itemgetter("question"),
                "output": self.prompt | self.model,
                "context": itemgetter("context"),
                "history": itemgetter("history")
            }
            # | StrOutputParser()
        )
        return chain
    
    def create_chain_with_history(self, retriever):
        chain = self.create_chain(retriever)
        
        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_session_history=self.get_session_history,
            input_messages_key="question",
            history_messages_key="history",
            history_factory_config=[
                ConfigurableFieldSpec(
                    id="user_id",
                    annotation=str,
                    name="User ID",
                    description="Unique identifier for the user.",
                    default="",
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id="conversation_id",
                    annotation=str,
                    name="Conversation ID",
                    description="Unique identifier for the conversation.",
                    default="",
                    is_shared=True,
                ),
            ],
        )
        return chain_with_history

    def get_session_history(self, user_id: str, conversation_id: str) -> BaseChatMessageHistory:
        if (user_id, conversation_id) not in self.history:
            self.history[(user_id, conversation_id)] = InMemoryHistory()
        return self.history[(user_id, conversation_id)]

    def ask_question(self, question: str):
        response = self.chain_with_history.invoke(
            {"question": question},
            config={"configurable": {"user_id": self.user_id, "conversation_id": self.conversation_id}}
        )
        print(response.get("output").content)
        print("\n")
        return response
