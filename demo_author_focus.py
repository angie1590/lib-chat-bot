#!/usr/bin/env python3
"""Demo visual del mejoramiento en búsquedas por autor"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from lib_chat_bot.catalog.models import Book
from lib_chat_bot.catalog.search_engine import score_book
from lib_chat_bot.catalog.intent_detector import detect_query_intent

# Cargar datos
df = pd.read_excel(Path(__file__).parent / 'SDLLista14nov2025.xlsx')
books = []
for idx, row in df.iterrows():
    if pd.notna(row.get("TITULO")):
        id_str = str(row.get("Cod. Item", ""))
        try:
            numeric_id = int(id_str) if id_str else idx
        except (ValueError, TypeError):
            numeric_id = idx

        book = Book(
            id=numeric_id,
            title=str(row.get("TITULO", "")).strip(),
            author=str(row.get("AUTOR", "")).strip() if pd.notna(row.get("AUTOR")) else "",
            isbn=str(row.get("ISBN", "")).strip() if pd.notna(row.get("ISBN")) else "",
            publisher=str(row.get("EDITORIAL", "")).strip() if pd.notna(row.get("EDITORIAL")) else "",
            category="",
            description="",
            stock=int(row.get("Existencia", 0)) if pd.notna(row.get("Existencia")) else 0,
        )
        books.append(book)

print("\n" + "="*80)
print("🎯 BÚSQUEDAS AHORA ENFOCADAS EN AUTOR")
print("="*80)

test_cases = [
    ("José ZAPATA", "Buscar libros ESCRITOS POR ZAPATA"),
    ("García maquez", "Buscar sobre García Márquez (con variación de caso)"),
]

for query, desc in test_cases:
    intent = detect_query_intent(query)
    print(f"\n📝 Query: '{query}'")
    print(f"   Intent: {intent.upper()}")
    print(f"   Descripción: {desc}")

    scores = [(score_book(b, query), b) for b in books]
    scores.sort(key=lambda x: x[0], reverse=True)

    print(f"\n   ✨ TOP 3 RESULTADOS (AHORA ENFOCADOS EN AUTOR):")
    for i, (score, book) in enumerate(scores[:3], 1):
        print(f"   {i}. [{score:4}] {book.title[:55]}")
        print(f"          Autor: {book.author[:50]}")

print("\n" + "="*80)
print("✅ Sistema enfocado en búsquedas por AUTOR")
print("="*80 + "\n")
