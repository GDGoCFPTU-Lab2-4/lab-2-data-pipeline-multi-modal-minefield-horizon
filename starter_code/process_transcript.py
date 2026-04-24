import re
import unicodedata

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Clean the transcript text and extract key information.

NUMBER_WORDS = {
    "khong": 0,
    "mot": 1,
    "moi": 1,
    "hai": 2,
    "ba": 3,
    "bon": 4,
    "tu": 4,
    "nam": 5,
    "lam": 5,
    "sau": 6,
    "bay": 7,
    "tam": 8,
    "chin": 9,
}

NUMBER_SEQUENCE_PATTERN = re.compile(
    r"\b((?:(?:khong|mot|moi|hai|ba|bon|tu|nam|lam|sau|bay|tam|chin|linh|le|muoi|tram|nghin|ngan|trieu|ty)\s+){1,10}"
    r"(?:muoi|tram|nghin|ngan|trieu|ty|khong|mot|moi|hai|ba|bon|tu|nam|lam|sau|bay|tam|chin))\b"
)


def _strip_accents(text):
    decomposed = unicodedata.normalize("NFD", text)
    without_accents = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return without_accents.replace("đ", "d").replace("Đ", "D")


def _normalize_vietnamese_text(text):
    normalized_text = _strip_accents(text.lower())
    normalized_text = re.sub(r"[^a-z0-9\s]", " ", normalized_text)
    return re.sub(r"\s+", " ", normalized_text).strip()


def _words_to_number(phrase):
    tokens = phrase.split()
    total = 0
    current = 0
    index = 0

    while index < len(tokens):
        token = tokens[index]
        if token in {"linh", "le"}:
            index += 1
            continue

        if token in NUMBER_WORDS:
            value = NUMBER_WORDS[token]
            next_token = tokens[index + 1] if index + 1 < len(tokens) else None

            if next_token == "tram":
                current += value * 100
                index += 2
                continue

            if next_token == "muoi":
                current += value * 10
                index += 2
                continue

            current += value
            index += 1
            continue

        if token == "muoi":
            current += 10
            index += 1
            continue

        if token in {"nghin", "ngan", "trieu", "ty"}:
            scale = {
                "nghin": 1_000,
                "ngan": 1_000,
                "trieu": 1_000_000,
                "ty": 1_000_000_000,
            }[token]
            current = current or 1
            total += current * scale
            current = 0
            index += 1
            continue

        index += 1

    return total + current


def _extract_price_from_vietnamese_words(text):
    normalized_text = _normalize_vietnamese_text(text)
    candidates = NUMBER_SEQUENCE_PATTERN.findall(normalized_text)
    for candidate in candidates:
        value = _words_to_number(candidate)
        if value >= 1_000:
            return value
    return None


def clean_transcript(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    # ------------------------------------------

    # TODO: Remove noise tokens like [Music], [inaudible], [Laughter]
    # TODO: Strip timestamps [00:00:00]
    # TODO: Find the price mentioned in Vietnamese words ("năm trăm nghìn")
    # TODO: Return a cleaned dictionary for the UnifiedDocument schema.

    cleaned_text = re.sub(r"\[\d{2}:\d{2}:\d{2}\]", " ", text)
    cleaned_text = re.sub(r"\[(?:Music(?: starts| ends)?|inaudible|Laughter)\]", " ", cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r"\[Speaker\s+\d+\]:?", " ", cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    detected_price = _extract_price_from_vietnamese_words(text)

    return {
        "document_id": "transcript-demo-001",
        "content": cleaned_text,
        "source_type": "Video",
        "author": "Unknown",
        "timestamp": None,
        "tags": ["transcript", "audio"],
        "source_metadata": {
            "original_file": "demo_transcript.txt",
            "detected_price_vnd": detected_price,
            "cleaning_steps": [
                "removed_timestamps",
                "removed_noise_tokens",
                "removed_speaker_labels",
            ],
        },
    }
