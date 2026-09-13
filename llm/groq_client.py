import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

from retrieval.retrieval import get_top_chunks

load_dotenv()

MODEL_NAME = "openai/gpt-oss-20b"
SYSTEM_PROMPT_PATH = Path(__file__).parent / "system_prompt.txt"

_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def _load_system_prompt():
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def _build_context(chunks):
    parts = []
    for chunk in chunks:
        parts.append(f"[Kaynak: {chunk['source']} - {chunk['title']}]\n{chunk['content']}")
    return "\n\n---\n\n".join(parts)


def answer_query(question):
    top_chunks = get_top_chunks(question, top_k=3)
    system_prompt = _load_system_prompt()

    if not top_chunks:
        # Retrieval eşik altında kaldı: LLM'e "bağlamda bilgi yok" sinyali.
        user_message = (
            "Bağlam: (Bu konuda bağlamda bilgi yok. "
            "Bilgi tabanında soruyla yeterince benzer bir kayıt bulunamadı.)\n\n"
            f"Soru: {question}"
        )
    else:
        context = _build_context(top_chunks)
        user_message = f"Bağlam:\n{context}\n\nSoru: {question}"

    response = _client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    question = "Manejde binme kuralları nelerdir?"
    answer = answer_query(question)
    print(f"Soru: {question}\n")
    print(f"Cevap: {answer}")