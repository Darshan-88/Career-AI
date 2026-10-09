from fastapi import UploadFile
from io import BytesIO


async def extract_resume_text(file: UploadFile) -> str:
    """
    Extract text from TXT, PDF and DOCX resume files.
    """

    filename = file.filename or ""
    extension = filename.lower().split(".")[-1]

    file_content = await file.read()

    # -------------------------
    # TXT files
    # -------------------------
    if extension == "txt":
        return file_content.decode("utf-8", errors="ignore")

    # -------------------------
    # PDF files
    # -------------------------
    elif extension == "pdf":
        try:
            from pypdf import PdfReader

            pdf_file = BytesIO(file_content)
            reader = PdfReader(pdf_file)

            text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            return text.strip()

        except Exception as e:
            raise ValueError(f"Could not read PDF file: {str(e)}")

    # -------------------------
    # DOCX files
    # -------------------------
    elif extension == "docx":
        try:
            from docx import Document

            docx_file = BytesIO(file_content)
            document = Document(docx_file)

            text = []

            for paragraph in document.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)

            return "\n".join(text).strip()

        except Exception as e:
            raise ValueError(f"Could not read DOCX file: {str(e)}")

    # -------------------------
    # Unsupported file
    # -------------------------
    else:
        raise ValueError(
            "Unsupported file type. Please upload a TXT, PDF or DOCX resume."
        )