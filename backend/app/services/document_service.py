def list_uploaded_documents() -> list[dict]:
    """
    List uploaded medical documents from the local storage folder.
    """

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    documents = []

    for filename in os.listdir(UPLOAD_DIR):
        if filename == ".gitkeep":
            continue

        file_path = os.path.join(UPLOAD_DIR, filename)

        if os.path.isfile(file_path):
            documents.append({
                "filename": filename,
                "path": file_path
            })

    return documents