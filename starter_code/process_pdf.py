import json
import os
import time

from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def _strip_code_fences(text):
    cleaned_text = text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
    return cleaned_text.strip()


def _generate_with_backoff(model, payload, max_attempts=4):
    delay_seconds = 1
    for attempt in range(1, max_attempts + 1):
        try:
            return model.generate_content(payload)
        except Exception as exc:
            error_message = str(exc)
            is_rate_limit = "429" in error_message or "rate limit" in error_message.lower()
            if is_rate_limit and attempt < max_attempts:
                time.sleep(delay_seconds)
                delay_seconds *= 2
                continue
            print(f"Failed to generate PDF content: {exc}")
            return None
    return None


def extract_pdf_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    if not GEMINI_API_KEY:
        print("Skipping PDF extraction because GEMINI_API_KEY is not configured.")
        return None

    try:
        import google.generativeai as genai
    except ImportError as exc:
        print(f"Skipping PDF extraction because google-generativeai is unavailable: {exc}")
        return None

    genai.configure(api_key=GEMINI_API_KEY)

    # Thay đổi model name để tránh lỗi 404 trên các phiên bản API cũ
    model = genai.GenerativeModel("gemini-2.5-flash")

    print(f"Uploading {file_path} to Gemini...")
    try:
        pdf_file = genai.upload_file(path=file_path)
    except Exception as exc:
        print(f"Failed to upload file to Gemini: {exc}")
        return None

    prompt = """
Analyze this PDF and extract Title, Author, Main Topics, any visible Tables, and a concise three-sentence summary.
Output exactly as a JSON object matching this exact format:
{
    "document_id": "pdf-doc-001",
    "content": "Summary: [Insert your 3-sentence summary here]",
    "source_type": "PDF",
    "author": "[Insert author name here]",
    "timestamp": null,
    "tags": ["pdf", "lecture-notes"],
    "source_metadata": {
        "original_file": "lecture_notes.pdf",
        "title": "[Insert title here]",
        "main_topics": ["topic 1", "topic 2"],
        "tables": ["table summary 1"]
    }
}
"""

    print("Generating content from PDF using Gemini...")
    response = _generate_with_backoff(model, [pdf_file, prompt])
    if response is None:
        return None

    try:
        extracted_data = json.loads(_strip_code_fences(response.text))
    except json.JSONDecodeError as exc:
        print(f"Failed to parse Gemini JSON response: {exc}")
        return None

    return extracted_data
