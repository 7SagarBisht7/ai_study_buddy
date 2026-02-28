from pypdf import PdfReader
import io

def extract_text_from_pdf(pdf_file):
    """Extract text content from uploaded PDF"""
    try:
        # Read PDF file
        pdf_reader = PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"