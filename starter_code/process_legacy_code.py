import ast
import re

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract docstrings and comments from legacy Python code.


def extract_logic_from_code(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()
    # ------------------------------------------

    # TODO: Use the 'ast' module to find docstrings for functions
    # TODO: (Optional/Advanced) Use regex to find business rules in comments like "# Business Logic Rule 001"
    # TODO: Return a dictionary for the UnifiedDocument schema.

    parsed_tree = ast.parse(source_code)
    module_docstring = ast.get_docstring(parsed_tree) or ""

    function_docstrings = {}
    for node in parsed_tree.body:
        if isinstance(node, ast.FunctionDef):
            function_docstring = ast.get_docstring(node)
            if function_docstring:
                function_docstrings[node.name] = function_docstring.strip()

    business_rule_mentions = re.findall(r"Business Logic Rule \d{3}", source_code)
    comment_lines = re.findall(r"#\s*(.+)", source_code)

    comment_rate_match = re.search(r"does\s+it\s+do\s+(\d+)%|does\s+(\d+)%", source_code, flags=re.IGNORECASE)
    comment_rate = next((int(group) for group in comment_rate_match.groups() if group), None) if comment_rate_match else None

    code_rate_match = re.search(r"tax_rate\s*=\s*([0-9.]+)", source_code)
    code_rate = float(code_rate_match.group(1)) * 100 if code_rate_match else None

    content_parts = []
    if module_docstring:
        content_parts.append(module_docstring.strip())
    for function_name, function_docstring in function_docstrings.items():
        content_parts.append(f"{function_name}: {function_docstring}")
    if comment_lines:
        content_parts.append("Comments: " + " | ".join(comment_lines))

    return {
        "document_id": "code-legacy-pipeline",
        "content": "\n\n".join(content_parts),
        "source_type": "Code",
        "author": "Senior Dev (retired)",
        "timestamp": None,
        "tags": ["legacy-code", "business-rules"],
        "source_metadata": {
            "original_file": "legacy_pipeline.py",
            "module_docstring": module_docstring.strip(),
            "function_docstrings": function_docstrings,
            "business_rule_mentions": business_rule_mentions,
            "comment_lines": comment_lines,
            "tax_comment_rate_percent": comment_rate,
            "tax_code_rate_percent": code_rate,
        },
    }
