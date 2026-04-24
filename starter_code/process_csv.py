import re

import pandas as pd

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Process sales records, handling type traps and duplicates.

NULL_LIKE_VALUES = {
    "",
    "n/a",
    "na",
    "null",
    "none",
    "liên hệ",
    "lien he",
}


def _normalize_text(value):
    return re.sub(r"\s+", " ", str(value).strip()).lower()


def _parse_price(value):
    if pd.isna(value):
        return None

    raw_value = str(value).strip()
    normalized_value = _normalize_text(raw_value)
    if normalized_value in NULL_LIKE_VALUES:
        return None

    if normalized_value == "five dollars":
        return 5.0

    cleaned_value = raw_value.replace(",", "")
    cleaned_value = re.sub(r"(?i)\b(vnd|usd)\b", "", cleaned_value)
    cleaned_value = cleaned_value.replace("$", "")
    cleaned_value = re.sub(r"[^\d.\-]", "", cleaned_value)
    if not cleaned_value or cleaned_value in {"-", ".", "-."}:
        return None

    try:
        return float(cleaned_value)
    except ValueError:
        return None


def _parse_sale_date(value):
    if pd.isna(value):
        return None

    cleaned_value = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", str(value).strip(), flags=re.IGNORECASE)
    known_formats = (
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%B %d %Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d %b %Y",
    )

    for fmt in known_formats:
        parsed_value = pd.to_datetime(cleaned_value, format=fmt, errors="coerce")
        if not pd.isna(parsed_value):
            return parsed_value.to_pydatetime()

    parsed_value = pd.to_datetime(cleaned_value, errors="coerce")
    if pd.isna(parsed_value):
        return None
    return parsed_value.to_pydatetime()


def process_sales_csv(file_path):
    # --- FILE READING (Handled for students) ---
    df = pd.read_csv(file_path)
    # ------------------------------------------

    # TODO: Remove duplicate rows based on 'id'
    # TODO: Clean 'price' column: convert "$1200", "250000", "five dollars" to floats
    # TODO: Normalize 'date_of_sale' into a single format (YYYY-MM-DD)
    # TODO: Return a list of dictionaries for the UnifiedDocument schema.

    cleaned_df = df.drop_duplicates(subset=["id"], keep="first").copy()
    documents = []

    for row in cleaned_df.to_dict(orient="records"):
        sale_timestamp = _parse_sale_date(row.get("date_of_sale"))
        parsed_price = _parse_price(row.get("price"))
        stock_quantity = row.get("stock_quantity")
        if pd.isna(stock_quantity):
            stock_quantity = None
        else:
            stock_quantity = int(stock_quantity)

        price_text = f"{parsed_price:.2f} {row.get('currency', '')}".strip() if parsed_price is not None else "an unavailable price"
        sold_on = sale_timestamp.strftime("%Y-%m-%d") if sale_timestamp else "an unknown date"

        documents.append(
            {
                "document_id": f"csv-{row['id']}",
                "content": (
                    f"Sales record for {row['product_name']} in category {row['category']} "
                    f"was recorded on {sold_on} with price {price_text}."
                ),
                "source_type": "CSV",
                "author": "Unknown",
                "timestamp": sale_timestamp,
                "tags": ["sales", "structured-data"],
                "source_metadata": {
                    "record_id": row["id"],
                    "product_name": row.get("product_name"),
                    "category": row.get("category"),
                    "price": parsed_price,
                    "raw_price": row.get("price"),
                    "currency": row.get("currency"),
                    "normalized_date_of_sale": sold_on if sale_timestamp else None,
                    "seller_id": row.get("seller_id"),
                    "stock_quantity": stock_quantity,
                },
            }
        )

    return documents
