"""
prepare_data.py
───────────────
Nettoie et prépare un dataset d'avis Amazon pour l'ingestion RAG.

Entrée  : fichier CSV brut (colonnes attendues : reviewText, summary, overall, asin)
Sortie  : fichier JSON prêt à être ingéré par le workflow n8n

Usage :
    python scripts/prepare_data.py --input data/raw_reviews.csv --output data/reviews_clean.json
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path


def clean_text(text: str) -> str:
    """Supprime le HTML résiduel, les espaces multiples et normalise le texte."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def process_reviews(input_path: str, output_path: str, min_length: int = 30) -> None:
    reviews = []
    skipped = 0

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            review_text = row.get("reviewText", "")
            if not review_text or len(review_text) < min_length:
                skipped += 1
                continue

            cleaned = clean_text(review_text)
            summary = clean_text(row.get("summary", ""))
            rating = float(row.get("overall", 0))
            product_id = row.get("asin", "unknown")

            reviews.append({
                "text": f"Note : {rating}/5 — {summary}\n{cleaned}",
                "metadata": {
                    "rating": rating,
                    "product_id": product_id,
                    "summary": summary,
                },
            })

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

    print(f"Terminé : {len(reviews)} avis exportés, {skipped} ignorés (< {min_length} car.)")
    print(f"Fichier : {output}")


def main():
    parser = argparse.ArgumentParser(description="Prépare les avis Amazon pour le RAG")
    parser.add_argument("--input", required=True, help="Chemin du CSV brut")
    parser.add_argument("--output", default="data/reviews_clean.json", help="Chemin de sortie JSON")
    parser.add_argument("--min-length", type=int, default=30, help="Longueur min. d'un avis (défaut: 30)")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Erreur : fichier introuvable → {args.input}", file=sys.stderr)
        sys.exit(1)

    process_reviews(args.input, args.output, args.min_length)


if __name__ == "__main__":
    main()
