import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain.schema.document import Document
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ConversationBufferMemory

from core.validate_prompt_injection import detect_prompt_injection

DB_PATH = "src/data/content_data.db"

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


def load_documents(db_path: str) -> list[Document]:
    conn = sqlite3.connect(db_path)
    query = "SELECT  title, content_md,url FROM content_data"
    df = pd.read_sql_query(query, conn)
    conn.close()

    documents = []
    for _, row in df.iterrows():
        documents.append(
            Document(
                page_content=row["content_md"],
                metadata={"title": row["title"], "url": row["url"]},
            )
        )

    return documents


def create_vector_store(documents: list[Document]) -> FAISS:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, length_function=len
    )
    split_docs = text_splitter.split_documents(documents)

    print(f"Documents: {len(documents)}. Created chunks: {len(split_docs)}.")

    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(split_docs, embeddings)

    return vector_store


def prompt_template() -> ChatPromptTemplate:
    template = """
        You are a helpful research assistant. Your task is to answer the user's question based solely on the provided context.

        Follow these rules strictly:
        1. Respond only based on the provided context, without making assumptions or additions.
        3. When you don't understand the question, ask for clarification instead of guessing.
        2. If the user asks for examples or references, use the chat history to understand what they are talking about, even if they do not explicitly repeat the subject.
        4. Look for chat history that may contain relevant information to answer the user's question.
        3. Look for code snippets in the context that start with "```" and end with "```", and use these code snippets to answer the user's question.
        4. If you do not find code snippets from the previous step, look for text examples in the context that may be useful to answer the user's question.
        5. Provide a friendly and direct answer to the user's question based on what you found.
        6. At the end of your answer, list ALL the URLs, without repeating, from the sources of the context snippets you used, under the phrase "If you need to check the reference used, take a look at these links:"
        7. If the context does not contain the answer, say "Sorry, I couldn't find information about this in my documents." and do not include any URL.

        Context:
        {context}

        User's Question:
        {question}
        
        Chat History:
        {history}

        Your Answer:
    """

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=openai_api_key)

    return prompt | llm | StrOutputParser()


def run_answer(
    question: str, vector_store: FAISS, memory: ConversationBufferMemory
) -> str:
    if detect_prompt_injection(question):
        return "🚫 Prompt Injection detected. Operation blocked."

    prompt = prompt_template()

    rag_query = vector_store.as_retriever(search_kwargs={"k": 5})

    messages = memory.chat_memory.messages
    history = ""
    for m in messages:
        history += f"{m.type}: {m.content}\n"

    response = prompt.invoke(
        {
            "context": rag_query.invoke(question),
            "question": question,
            "history": history,
        }
    )

    return response
