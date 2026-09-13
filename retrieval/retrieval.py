import re
import numpy as np
from sentence_transformers import SentenceTransformer

from db.database import get_all_chunks

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# Cosine benzerliği bu değerin altındaysa chunk alakasız sayılır.
# En iyi skor bile eşiğin altındaysa hiç chunk dönülmez (boş context).
SIMILARITY_THRESHOLD = 0.40

# Soru kelimesi başlıkta geçiyorsa cosine'a eklenecek bonus.
# "atımı nasıl tımar ederim" gibi sorularda embedding, tımar chunk'ı
# yerine başlık/eyer chunk'larını öne çıkarabiliyor; kelime eşlemesi bunu düzeltir.
TITLE_TERM_BONUS = 0.15
CONTENT_TERM_BONUS = 0.05
MAX_LEXICAL_BONUS = 0.30

_STOPWORDS = {
    "nasıl", "nedir", "neden", "hangi", "niçin", "niye", "için", "gibi",
    "kadar", "ederim", "etmeliyim", "etmelidir", "yapılır", "yapmalıyım",
    "olmalı", "olmalıdır", "nelerdir", "neler", "bugün", "mıdır", "midir",
}

# FastAPI sürecinde dosya bir kez import edilir; model bellekte kalır.
model = SentenceTransformer(MODEL_NAME)


def _cosine_similarity(vector_a, vector_b):
    a = np.array(vector_a)
    b = np.array(vector_b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


_TR_FOLD = str.maketrans({
    "ı": "i",
    "İ": "i",
    "I": "i",
    "ş": "s",
    "Ş": "s",
    "ğ": "g",
    "Ğ": "g",
    "ü": "u",
    "Ü": "u",
    "ö": "o",
    "Ö": "o",
    "ç": "c",
    "Ç": "c",
    "â": "a",
    "î": "i",
    "û": "u",
})


def _fold(text):
    # Python casefold Türkçe I/ı ayrımını bozar: "tımar" != "TIMAR".casefold()
    return text.translate(_TR_FOLD).lower()


def _query_terms(question):
    tokens = re.findall(r"[0-9a-zA-Z]+", _fold(question))
    stop = {_fold(s) for s in _STOPWORDS}
    return [t for t in tokens if len(t) >= 4 and t not in stop]


def _lexical_bonus(terms, chunk):
    if not terms:
        return 0.0
    title = _fold(chunk["title"])
    content = _fold(chunk["content"])
    bonus = 0.0
    for term in terms:
        if term in title:
            bonus += TITLE_TERM_BONUS
        elif term in content:
            bonus += CONTENT_TERM_BONUS
    return min(bonus, MAX_LEXICAL_BONUS)


def get_top_chunks(question, top_k=3, threshold=SIMILARITY_THRESHOLD):
    question_embedding = model.encode(question)
    terms = _query_terms(question)

    all_chunks = get_all_chunks()

    scored_chunks = []
    for chunk in all_chunks:
        cosine = float(_cosine_similarity(question_embedding, chunk["embedding"]))
        combined = cosine + _lexical_bonus(terms, chunk)
        scored_chunks.append((combined, cosine, chunk))

    # Eşik ham cosine'a bakılır: kelime bonusu kapsam dışı soruları şişirmesin.
    scored_chunks = [row for row in scored_chunks if row[1] >= threshold]
    scored_chunks.sort(key=lambda row: row[0], reverse=True)

    if not scored_chunks:
        return []

    top_chunks = scored_chunks[:top_k]
    return [{"score": cosine, "rank_score": combined, **chunk} for combined, cosine, chunk in top_chunks]


if __name__ == "__main__":
    question = "Manejde binme kuralları nelerdir?"
    results = get_top_chunks(question)

    print(f"Question: {question}\n")
    if not results:
        print("Eşik altında: bağlam boş (bilgi tabanında yeterince benzer chunk yok).")
    else:
        for r in results:
            print(f"Score: {r['score']:.3f} | Title: {r['title']} | Source: {r['source']}")
            print(r["content"][:150], "...")
            print("-" * 60)
