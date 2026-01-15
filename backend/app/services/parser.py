import io
from pypdf import PdfReader
from fastapi import UploadFile, HTTPException

async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extracts text from an uploaded file (TXT or PDF).
    """
    filename = file.filename.lower()
    content = await file.read()
    
    if filename.endswith(".txt"):
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
             # Fallback to latin-1 if utf-8 fails
            return content.decode("latin-1")
            
    elif filename.endswith(".pdf"):
        try:
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
            
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload .txt or .pdf")
