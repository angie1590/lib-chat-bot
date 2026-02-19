#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from lib_chat_bot.catalog.models import Book
from lib_chat_bot.catalog.search_engine import score_book, rerank_books
from lib_chat_bot.catalog.intent_detector import detect_query_intent

# Cargar datos
df = pd.read_excel(Path(__file__).parent / 'SDLLista14nov2025.xlsx')
books_data = []
for idx, row in df.iterrows():
    id_str = str(row['Cod. Item'])
    numeric_id = abs(hash(id_str)) % (10 ** 9)
    title = row['TITULO'] if pd.notna(row['TITULO']) else ''
    author = row['AUTOR'] if pd.notna(row['AUTOR']) else None
    publisher = row['EDITORIAL'] if pd.notna(row['EDITORIAL']) else None
    isbn = row['ISBN'] if pd.notna(row['ISBN']) else None
    if not title:
        continue
    book = Book(
        id=numeric_id,
        title=str(title),
        author=str(author) if author else None,
        publisher=str(publisher) if publisher else None,
        isbn=str(isbn) if isbn else None,
        stock=int(row['Existencia']) if pd.notna(row['Existencia']) else 0,
    )
    books_data.append(book)

query = "quiero libros que hablen de García Márquez"
print(f"Query: '{query}'")
print(f"Total de libros en BD: {len(books_data)}\n")

intent = detect_query_intent(query)
query_words = set(query.lower().split())
matching_books = []

print(f"Intent detectado: {intent}")
print(f"Palabras de búsqueda: {query_words}\n")

for book in books_data:
    title_lower = (book.title or '').lower()
    author_lower = (book.author or '').lower()

    # Buscar palabras > 2 caracteres en título o autor
    for word in query_words:
        if len(word) > 2 and (word in title_lower or word in author_lower):
            matching_books.append(book)
            break

print(f"Libros encontrados (pre-filtering): {len(matching_books)}")
print()

if matching_books:
    ranked = rerank_books(matching_books, query)
    print("Top 10 resultados:")
    for i, book in enumerate(ranked[:10], 1):
        score = score_book(book, query)
        print(f"{i}. {book.title:50} | {book.author:30} | Score: {score:6.0f}")
else:
    print("No se encontraron resultados")
