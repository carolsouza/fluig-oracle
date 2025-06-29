import streamlit as st
from langchain.memory import ConversationBufferMemory
from core.langchain_rag import run_answer, load_documents, create_vector_store
from langchain_community.vectorstores import FAISS

MEMORY = ConversationBufferMemory()
DB_PATH = "src/data/content_data.db"

def get_vector_store() -> FAISS:
    if "vector_store" not in st.session_state:
        docs = load_documents(DB_PATH)
        st.session_state["vector_store"] = create_vector_store(docs)
    return st.session_state["vector_store"]

def show_chat_history(memoria):
    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

def chat_page():
    st.header("🤖 Chat with Fluig Oracle")
    vector_store = get_vector_store()
    memory = st.session_state.get('memory', MEMORY)
    show_chat_history(memory)

    user_input = st.chat_input('Ask me something about Fluig!')
    if user_input:
        st.chat_message('human').markdown(user_input)
        try:
            answer = run_answer(user_input, vector_store=vector_store, memory=memory)
        except Exception as e:
            answer = f"Something went wrong: {e}"
        st.chat_message('ai').markdown(answer)
        memory.chat_memory.add_user_message(user_input)
        memory.chat_memory.add_ai_message(answer)
        st.session_state['memory'] = memory
        
def main():
    chat_page()

if __name__ == '__main__':
    main()