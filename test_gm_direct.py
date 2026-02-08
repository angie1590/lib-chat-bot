#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from lib_chat_bot.catalog.models import Book
from lib_chat_bot.catalog.search_engine import score_book
from lib_chat_bot.catalog.intent_detector import detect_query_intent

# Cargar datos
df = pd.read_excel(Path(__file__).parent / 'SDLLista14nov2025.xlsx')

# Filtrar solo libros de García Márquez
gm_df = df[df['AUTOR'].str.contains('GARCIA MARQUEZ, GABRIEL', case=False, na=False, regex=False)]
print(f"Libros de García Márquez en la BD: {len(gm_df)}\n")

# Convertir a objetos Book
books_data = []
for idx, row in gm_df.iterrows():
    id_str = str(row['Cod. Item'])
    numeric_id = abs(hash(id_str)) % (10 ** 9)
    title = row['TITULO'] if pd.notna(row['TITULO']) else ''
    author = row['AUTOR'] if pd.notna(row['AUTOR']) else None
    publisher = row['EDITORIAL'] if pd.notna(row['EDITORIAL']) else None
    if not title:
        continue
    book = Book(
        id=numeric_id,
        title=str(title),
        author=str(author) if author else None,
        publisher=str(publisher) if publisher else None,
        stock=int(row['Existencia']) if pd.notna(row['Existencia']) else 0,
    )
    books_data.append(book)

# Probar búsqueda
query = "García maquez"
intent = detect_query_intent(query)

print(f"Búsqueda: '{query}'")
print(f"Intent detectado: {intent}\n")
print("=" * 80)

scored = [(score_book(b, query), b) for b in books_data]
scored.sort(key=lambda x: x[0], reverse=True)

print("Top 5 resultados de García Márquez:\n")
for i, (score, book) in enumerate(scored[:5], 1):
    print(f"{i}. [{score:4d}] {book.title}")
    print(f"         Autor: {book.author}\n")
