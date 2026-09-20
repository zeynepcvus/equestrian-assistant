# 🐴 Binici Asistanı

Binicilerin ahırda veya manejde at bakımı, ekipman ve biniş kuralları hakkında soru sorup anında cevap alabileceği, RAG (Retrieval-Augmented Generation) tabanlı bir Türkçe soru-cevap asistanı.

## Ne yapıyor?

Kullanıcı bir soru sorduğunda, sistem önce kendi bilgi tabanından en alakalı bilgiyi bulur, sonra bu bilgiye dayanarak (uydurmadan) bir cevap üretir. Bilgi tabanında olmayan konularda "bilmiyorum" der; sağlık/tedavi konularında veteriner hekime yönlendirir.

## Mimari

```
Kullanıcı (web arayüzü)
      │  POST /ask
      ▼
Backend (FastAPI)
      │
      ▼
Retrieval (embedding + cosine similarity)
      │
      ▼
SQLite (361 chunk, bilgi tabanından üretildi)
      │
      ▼
LLM (Groq API) → cevap
```

## Teknoloji Kararları

| Bileşen | Seçim | Neden |
|---|---|---|
| Framework | Yok — sıfırdan Python | Her adımı anlayarak öğrenmek için; LangChain gibi hazır bir framework yerine tercih edildi |
| Embedding | `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`) | Ücretsiz, Türkçe destekli |
| Vektör arama | `numpy` ile cosine similarity | Küçük veri seti için yeterli, ekstra bağımlılık gerekmiyor |
| Veritabanı | SQLite | Sunucu gerektirmez, tek dosya |
| LLM | Groq API (`openai/gpt-oss-20b`) | Ücretsiz, hızlı |
| Backend | FastAPI | Frontend'den bağımsız, HTTP üzerinden servis |
| Frontend | Özel HTML/CSS/JS | Tam görsel kontrol için Streamlit'ten geçildi |
| Yerel Foundry | Kullanılmadı | Ödevde örnek olarak verildi, zorunlu değildi; ücretsiz bulut deployment'a uygun değil |

## Proje Yapısı

```
├── data/kaynaklar/     # Bilgi tabanı (.txt, **Başlık** formatlı)
├── db/                 # SQLite katmanı
├── ingestion/          # Chunking + embedding üretme
├── retrieval/          # Benzerlik araması
├── llm/                # Groq entegrasyonu + sistem promptu
├── backend/            # FastAPI servisi
├── web/                # Frontend (HTML/CSS/JS)
└── archive/            # Eski Streamlit prototipi
```

## Kurulum

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

`.env.example` dosyasını `.env` olarak kopyala, `GROQ_API_KEY` ve `APP_PASSWORD` değerlerini gir.

Bilgi tabanını veritabanına işle:
```bash
python -m ingestion.ingest
```

## Çalıştırma

İki terminal gerekir:

```bash
# Terminal 1 — Backend
python -m uvicorn backend.main:app --reload

# Terminal 2 — Frontend
cd web
python -m http.server 5500
```

Tarayıcıda `http://localhost:5500` adresini aç.

## Bilinen Sınırlamalar

- Retrieval bazen alakasız bir chunk'ı top-3'e sokabiliyor; bir benzerlik eşiği (0.40) ile bu büyük ölçüde azaltıldı, ama tam kusursuz değil.
- Sistem şu an yalnızca yerelde (localhost) çalışıyor — deployment (Render, ücretsiz tier) planlandı, henüz tamamlanmadı.
- Ücretsiz LLM/hosting kotalarına tabi.

## Gelecek Geliştirmeler

- Render üzerinde canlıya alma
- Kaynak gösterme (cevapta hangi dokümandan geldiği)
- 20-30 soruluk test seti ile accuracy ölçümü
- PostgreSQL + pgvector'e geçiş (çok kullanıcılı senaryoda)
