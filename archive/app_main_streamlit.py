import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from llm.groq_client import answer_query

st.set_page_config(
    page_title="Binici Asistanı",
    page_icon="🐴",
    layout="centered",
)

CUSTOM_CSS = """
<style>
.stApp {
    background-color: #FAF3E3;
}

section[data-testid="stSidebar"] {
    background-color: #EFE0C3;
}

h1 {
    color: #5C3A21;
    font-weight: 700;
}

[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 4px 8px;
}

div[data-testid="stChatInput"] textarea {
    border: 1px solid #C9A574;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🐴 Binici Asistanı")
    st.markdown(
        "Ahırda veya manejde aklına takılan sorular için buradayım. "
        "At bakımı, ekipman, biniş kuralları ve daha fazlası hakkında sorabilirsin."
    )
    st.markdown("---")
    if st.button("Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

st.title("🐴 Binici Asistanı")
st.caption("Ahır ve manej hakkında sorularını yanıtlıyorum.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "🧑" if message["role"] == "user" else "🐴"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

question = st.chat_input("Sorunu yaz...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🐴"):
        with st.spinner("Düşünüyorum..."):
            answer = answer_query(question)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
