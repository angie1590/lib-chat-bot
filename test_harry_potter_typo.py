#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from lib_chat_bot.catalog.models import Book
from lib_chat_bot.catalog.search_engine import score_book, rerank_books
from lib_chat_bot.catalog.intent_detector import detect_query_intent

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

query = "jarry poter 1"
print(f"Query: '{query}'")
print("=" * 80)

intent = detect_query_intent(query)
query_words = set(query.lower().split())
matching_books = []

print(f"Intent: {intent}")
print(f"Palabras: {query_words}\n")

for book in books_data:
    title_lower = (book.title or '').lower()
    author_lower = (book.author or '').lower()
    
    for word in query_words:
        if len(word) > 2 and (word in title_lower or word in author_lower):
            matching_books.append(book)
            break

print(f"Libros encontrados (pre-filter): {len(matching_books)}")
print()

if matching_books:
    ranked = rerank_books(matching_books, query)
    for i, book in enumerate(ranked[:10], 1):
        score = score_book(book, query)
        author_str = book.author if book.author else "N/A"
        print(f"{i}. {book.title[:55]:55} | {author_str[:20]:20} | Score: {score:6.0f}")
else:
    print("No results found")
