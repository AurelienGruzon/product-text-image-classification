#!/usr/bin/env python3

import requests
import pandas as pd

def safe_first(*values):
    """Return the first non-empty value among candidates."""
    for v in values:
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        return v
    return None

def fetch_openfoodfacts_products(query: str, page_size: int = 50):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("products", [])

def map_to_required_fields(p: dict) -> dict:
    """
    Map OpenFoodFacts product JSON -> required CSV columns:
    foodId, label, category, foodContentsLabel, image
    """
    food_id = p.get("code")

    label = safe_first(
        p.get("product_name_fr"),
        p.get("product_name"),
        p.get("generic_name_fr"),
        p.get("generic_name"),
    )

    category = safe_first(
        p.get("categories"),
        ", ".join(p.get("categories_tags", [])) if p.get("categories_tags") else None,
    )

    food_contents_label = safe_first(
        p.get("ingredients_text_fr"),
        p.get("ingredients_text"),
        p.get("ingredients_text_with_allergens_fr"),
        p.get("ingredients_text_with_allergens"),
    )

    image = safe_first(
        p.get("image_front_url"),
        p.get("image_url"),
        p.get("image_front_small_url"),
    )

    return {
        "foodId": food_id,
        "label": label,
        "category": category,
        "foodContentsLabel": food_contents_label,
        "image": image,
    }


def main():
    products = fetch_openfoodfacts_products("champagne", page_size=50)

    rows = []
    for p in products:
        row = map_to_required_fields(p)

        if row["foodId"] and row["label"] and row["image"]:
            rows.append(row)

        if len(rows) == 10:
            break

    df_champagne = pd.DataFrame(
        rows,
        columns=["foodId", "label", "category", "foodContentsLabel", "image"],
    )

    print(df_champagne)
    output = "../data/champagne_openfoodfacts.csv"
    df_champagne.to_csv(output, index=False)
    print("Saved:", output)


if __name__ == "__main__":
    main()