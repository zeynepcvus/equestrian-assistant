from pathlib import Path
from sentence_transformers import SentenceTransformer

from db.database import create_database, clear_database, save_chunk

SOURCES_FOLDER = Path(__file__).parent.parent / "data" / "kaynaklar"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def _is_heading(line):
    s = line.strip()
    return s.startswith("**") and s.endswith("**") and s.count("**") == 2


def _clean_heading(line):
    return line.strip().strip("*").strip()


def chunk_file(file_path):
    text = file_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    chunks = []
    current_title = None
    current_lines = []

    def close_chunk():
        content = "\n".join(current_lines).strip()
        if not content:
            return
        if current_title:
            content = f"{current_title}\n{content}"
        chunks.append({
            "content": content,
            "title": current_title,
            "source": file_path.name,
        })

    for line in lines:
        if _is_heading(line):
            close_chunk()
            current_title = _clean_heading(line)
            current_lines = []
        else:
            current_lines.append(line)

    close_chunk()
    return chunks


def chunk_all_files():
    chunks = []
    for file_path in sorted(SOURCES_FOLDER.glob("*.txt")):
        chunks.extend(chunk_file(file_path))
    return chunks


def run_ingestion():
    print("Chunking files...")
    chunks = chunk_all_files()
    print(f"Total chunks: {len(chunks)}")

    print(f"Loading embedding model ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)

    print("Generating embeddings (this may take a moment)...")
    texts = [chunk["content"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    print("Resetting database...")
    create_database()
    clear_database()

    print("Saving chunks to database...")
    for chunk, embedding in zip(chunks, embeddings):
        save_chunk(
            content=chunk["content"],
            embedding=embedding.tolist(),
            source=chunk["source"],
            title=chunk["title"],
        )

    print("Done.")


if __name__ == "__main__":
    run_ingestion()