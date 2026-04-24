# ==========================================
# ROLE 3: OBSERVABILITY & QA ENGINEER
# ==========================================
# Task: Implement quality gates to reject corrupt data or logic discrepancies.

TOXIC_STRINGS = (
    "null pointer exception",
    "traceback",
    "fatal error",
    "segmentation fault",
    "stack trace",
)


def run_quality_gate(document_dict):
    # TODO: Reject documents with 'content' length < 20 characters
    # TODO: Reject documents containing toxic/error strings (e.g., 'Null pointer exception')
    # TODO: Flag discrepancies (e.g., if tax calculation comment says 8% but code says 10%)

    # Return True if pass, False if fail.

    content = str(document_dict.get("content", "")).strip()
    if len(content) < 20:
        print(f"Quality gate rejected {document_dict.get('document_id', 'unknown-doc')}: content too short.")
        return False

    lowered_content = content.lower()
    if any(toxic_string in lowered_content for toxic_string in TOXIC_STRINGS):
        print(f"Quality gate rejected {document_dict.get('document_id', 'unknown-doc')}: toxic/error content detected.")
        return False

    source_metadata = document_dict.get("source_metadata", {}) or {}
    comment_rate = source_metadata.get("tax_comment_rate_percent")
    code_rate = source_metadata.get("tax_code_rate_percent")
    if comment_rate is not None and code_rate is not None and float(comment_rate) != float(code_rate):
        print(
            f"Quality gate rejected {document_dict.get('document_id', 'unknown-doc')}: "
            f"tax rule discrepancy detected ({comment_rate}% comment vs {code_rate}% code)."
        )
        return False

    return True
