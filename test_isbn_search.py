#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from lib_chat_bot.catalog.models import Book
from lib_chat_bot.catalog.search_engine import score_book, fuzzy_score_author, rerank_books
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

print(f"Loaded {len(books_data)} books\n")

# Probar ISBNs
test_isbns = ['9786287641969', '9786287641890']

for isbn_query in test_isbns:
    print(f"Buscando ISBN: {isbn_query}")
    print("=" * 60)
    
    intent = detect_query_intent(isbn_query)
    matching_books = []
    
    for book in books_data:
        isbn_clean = (book.isbn or '').replace('-', '').replace(' ', '')
        query_clean = isbn_query.replace('-', '').replace(' ', '')
        
        if intent == "isbn":
            if isbn_clean == query_clean:
                matching_books.append(book)
    
    if matching_books:
        ranked = rerank_books(matching_books, isbn_query)
        for i, book in enumerate(ranked[:5], 1):
            score = score_book(book, isbn_query)
            print(f"{i}. {book.title} | Autor: {book.author} | Score: {score}")
    else:
        print("   No se encontraron resultados")
    
    print()
