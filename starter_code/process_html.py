import re

from bs4 import BeautifulSoup

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract product data from the HTML table, ignoring boilerplate.

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


def _parse_catalog_price(value):
    raw_value = str(value).strip()
    if _normalize_text(raw_value) in NULL_LIKE_VALUES:
        return None

    cleaned_value = raw_value.replace(",", "")
    cleaned_value = re.sub(r"(?i)\b(vnd|usd)\b", "", cleaned_value)
    cleaned_value = re.sub(r"[^\d.\-]", "", cleaned_value)
    if not cleaned_value:
        return None

    try:
        return float(cleaned_value)
    except ValueError:
        return None


def parse_html_catalog(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    # ------------------------------------------

    # TODO: Use BeautifulSoup to find the table with id 'main-catalog'
    # TODO: Extract rows, handling 'N/A' or 'Liên hệ' in the price column.
    # TODO: Return a list of dictionaries for the UnifiedDocument schema.

    table = soup.find("table", id="main-catalog")
    if table is None or table.tbody is None:
        return []

    documents = []
    for row in table.tbody.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
        if len(cells) != 6:
            continue

        product_id, product_name, category, raw_price, stock_text, rating_text = cells
        parsed_price = _parse_catalog_price(raw_price)

        try:
            stock_quantity = int(stock_text)
        except ValueError:
            stock_quantity = None

        price_text = f"{parsed_price:.2f} VND" if parsed_price is not None else f"price unavailable ({raw_price})"
        stock_status = str(stock_quantity) if stock_quantity is not None else "unknown"
        rating_status = rating_text or "unrated"

        documents.append(
            {
                "document_id": f"html-{product_id}",
                "content": (
                    f"Catalog entry for {product_name} in category {category} lists the product at {price_text}, "
                    f"with stock level {stock_status} and rating {rating_status}."
                ),
                "source_type": "HTML",
                "author": "VinShop Catalog",
                "timestamp": None,
                "tags": ["catalog", "web"],
                "source_metadata": {
                    "product_id": product_id,
                    "product_name": product_name,
                    "category": category,
                    "price": parsed_price,
                    "raw_price": raw_price,
                    "stock_quantity": stock_quantity,
                    "rating": rating_text,
                },
            }
        )

    return documents
