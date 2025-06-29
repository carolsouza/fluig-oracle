import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.document import Document
from langchain.schema.output_parser import StrOutputParser

from langchain.memory import ConversationBufferMemory

DB_PATH = "src/data/content_data.db"

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def load_documents(db_path: str) -> list[Document]:
    """
    Load documents from the SQLite database.
    """
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
    """
    Create a vector store from the documents using FAISS.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, length_function=len
    )
    split_docs = text_splitter.split_documents(documents)

    print(
        f"Total de documentos: {len(documents)}. Total de chunks criados: {len(split_docs)}."
    )

    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(split_docs, embeddings)

    return vector_store


def prompt_template() -> ChatPromptTemplate:
    """
    Create a prompt template for the RAG system.
    """

    template = """
        Você é um assistente de pesquisa prestativo. Sua tarefa é responder à pergunta do usuário baseando-se unicamente no contexto fornecido.
        
        Siga estas regras estritamente:
        1. Entenda que o histórico é uma coleção de mensagens anteriores que podem ser usadas junto ao contexto para responder a pergunta atual.
        3. Use o histórico para saber o que está sendo discutido e com base informações relevantes no contexto fornecido.
        4. Se o usuário pedir exemplos ou referências, use o histórico da conversa para entender sobre o que ele está falando, mesmo que ele não repita explicitamente o assunto.
        5. Procure por trechos de código no contexto que comecem com "```" e terminam com "```", e use esses trechos de código para responder à pergunta do usuário.
        6. Se não encontrar trechos de código do passo anterior busque exemplos em texto que possam ser úteis para responder à pergunta do usuário.
        6. Responda apenas com base no contexto e no histórico fornecido, sem fazer suposições ou adições.
        7. Forneça uma resposta amigável e direta à pergunta do usuário com base no que encontrou.
        8. No final da sua resposta, liste TODAS as URLs, sem repetir, de origem dos trechos de contexto que você usou, sob a frase "Se precisar visualizar a fonte original, dê uma olhada nestes links:".
        9. Se o contexto não contiver a resposta, diga "Desculpe, não encontrei informações sobre isso nos meus documentos." e não inclua nenhuma URL.

        Contexto:
        {context}

        Pergunta do Usuário:
        {question}
        
        Histórico:
        {memory}

        Sua Resposta:
    """

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=openai_api_key)

    return (
        prompt
        | llm
        | StrOutputParser()
        | RunnablePassthrough(
            output_key="answer",
        )
    )
    
def run_answer(question: str, vector_store:FAISS, memory: ConversationBufferMemory) -> str:
    prompt = prompt_template()
    
    rag_query = vector_store.as_retriever(search_kwargs={"k": 5})
    
    messages = memory.chat_memory.messages
    history = ""
    for m in messages:
        history += f"{m.type}: {m.content}\n"
    
    response = prompt.invoke(
        {"context": rag_query.invoke(history + question), "question": question, "memory": history}
    )
    
    return response