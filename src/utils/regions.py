from __future__ import annotations

import re


FEDERAL_DISTRICT_PATTERN = re.compile(r"федеральный округ", flags=re.IGNORECASE)


def normalize_region_name(value: str) -> str:
    """
    Normalize region names from Rosstat tables.
    """
    text = str(value).strip()
    text = re.sub(r"\d+\)$", "", text).strip()
    text = re.sub(r"\s+", " ", text)

    replacements = {
        "г.Москва": "г. Москва",
        "г.Санкт-Петербург": "г. Санкт-Петербург",
        "авт.область": "авт. область",
        "авт.округ": "авт. округ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def classify_territory_level(region_name: str) -> str:
    """
    Classify row as 'federal_district' or 'subject'.
    """
    if FEDERAL_DISTRICT_PATTERN.search(region_name):
        return "federal_district"
    return "subject"


def is_federal_district(region_name: str) -> bool:
    """
    Return True if the region name belongs to a federal district.
    """
    return classify_territory_level(region_name) == "federal_district"