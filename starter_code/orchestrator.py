import json
import os
import time

# Robust path handling
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "raw_data")


# Import role-specific modules
from schema import UnifiedDocument
from process_pdf import extract_pdf_data
from process_transcript import clean_transcript
from process_html import parse_html_catalog
from process_csv import process_sales_csv
from process_legacy_code import extract_logic_from_code
from quality_check import run_quality_gate

# ==========================================
# ROLE 4: DEVOPS & INTEGRATION SPECIALIST
# ==========================================
# Task: Orchestrate the ingestion pipeline and handle errors/SLA.


def _ensure_list(result):
    if result is None:
        return []
    if isinstance(result, list):
        return result
    return [result]


def _serialize_document(document):
    if hasattr(document, "model_dump"):
        return document.model_dump(mode="json")
    return json.loads(document.json())


def _collect_documents(final_kb, processor_name, raw_documents):
    for raw_document in _ensure_list(raw_documents):
        if not raw_document:
            continue

        try:
            document = UnifiedDocument(**raw_document)
        except Exception as exc:
            print(f"Skipping invalid document from {processor_name}: {exc}")
            continue

        serialized_document = _serialize_document(document)
        if run_quality_gate(serialized_document):
            final_kb.append(serialized_document)


def main():
    start_time = time.time()
    final_kb = []

    # --- FILE PATH SETUP (Handled for students) ---
    pdf_path = os.path.join(RAW_DATA_DIR, "lecture_notes.pdf")
    trans_path = os.path.join(RAW_DATA_DIR, "demo_transcript.txt")
    html_path = os.path.join(RAW_DATA_DIR, "product_catalog.html")
    csv_path = os.path.join(RAW_DATA_DIR, "sales_records.csv")
    code_path = os.path.join(RAW_DATA_DIR, "legacy_pipeline.py")

    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "processed_knowledge_base.json")
    # ----------------------------------------------

    # TODO: Call each processing function (extract_pdf_data, clean_transcript, etc.)
    # TODO: Run quality gates (run_quality_gate) before adding to final_kb
    # TODO: Save final_kb to output_path using json.dump

    processing_steps = [
        ("extract_pdf_data", extract_pdf_data, pdf_path),
        ("clean_transcript", clean_transcript, trans_path),
        ("parse_html_catalog", parse_html_catalog, html_path),
        ("process_sales_csv", process_sales_csv, csv_path),
        ("extract_logic_from_code", extract_logic_from_code, code_path),
    ]

    for processor_name, processor_fn, source_path in processing_steps:
        try:
            processed_documents = processor_fn(source_path)
            _collect_documents(final_kb, processor_name, processed_documents)
        except Exception as exc:
            print(f"Processor {processor_name} failed for {source_path}: {exc}")

    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(final_kb, output_file, ensure_ascii=False, indent=2)

    end_time = time.time()
    print(f"Pipeline finished in {end_time - start_time:.2f} seconds.")
    print(f"Total valid documents stored: {len(final_kb)}")


if __name__ == "__main__":
    main()
