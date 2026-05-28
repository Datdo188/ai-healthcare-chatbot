import os
import re
from pathlib import Path

from app.services.rag_index_service import index_document_chunks


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 150
) -> list[str]:
    text = clean_text(text)

    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - chunk_overlap

    return chunks


def index_raw_documents() -> dict:
    raw_dir = Path(os.getenv("RAW_DOCS_DIR", "/app/data/raw"))

    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw docs folder not found: {raw_dir}")

    txt_files = sorted(raw_dir.glob("*.txt"))

    if not txt_files:
        return {
            "raw_dir": str(raw_dir),
            "total_files": 0,
            "total_chunks": 0,
            "indexed_files": [],
            "message": "No .txt files found."
        }

    total_chunks = 0
    indexed_files = []

    # user_id = 0 means global medical knowledge base
    global_knowledge_user_id = 0

    for file_path in txt_files:
        text = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        chunks = chunk_text(text)

        result = index_document_chunks(
            filename=file_path.name,
            chunks=chunks,
            user_id=global_knowledge_user_id
        )

        indexed_chunks = result.get("indexed_chunks", 0)

        total_chunks += indexed_chunks

        indexed_files.append({
            "filename": file_path.name,
            "chunks": indexed_chunks
        })

    return {
        "raw_dir": str(raw_dir),
        "total_files": len(indexed_files),
        "total_chunks": total_chunks,
        "indexed_files": indexed_files,
        "message": "Raw medical documents indexed successfully."
    }


def main():
    result = index_raw_documents()

    print(result["message"])
    print(f"Raw directory: {result['raw_dir']}")
    print(f"Total files indexed: {result['total_files']}")
    print(f"Total chunks indexed: {result['total_chunks']}")

    for item in result["indexed_files"]:
        print(f"- {item['filename']}: {item['chunks']} chunks")


if __name__ == "__main__":
    main()