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

# Pruebas
test_queries = [
    'Gestion Anbiental',
    'José ZAPATA',
    'García maquez',
    'rowlin',
    'jk rowlin',
    'isabella Ayende',
    '9781567182811',
    'Ensayos breves para la relijion',
    'FUCOL, MICHEL',
]

for query in test_queries:
    print('=' * 80)
    print(f'Consulta: {query}')
    print('=' * 80)

    intent = detect_query_intent(query)
    query_words = set(query.lower().split())
    matching_books = []

    for book in books_data:
        title_lower = (book.title or '').lower()
        author_lower = (book.author or '').lower()
        isbn_clean = (book.isbn or '').replace('-', '').replace(' ', '')

        if intent == "isbn":
            # ISBN search: exact match only
            query_clean = query.replace('-', '').replace(' ', '')
            if isbn_clean == query_clean:
                matching_books.append(book)
        elif intent == "author":
            author_score = fuzzy_score_author(query, book.author or "", threshold=75)
            if author_score >= 75:
                matching_books.append(book)
        else:
            for word in query_words:
                if len(word) > 2 and (word in title_lower or word in author_lower):
                    matching_books.append(book)
                    break

    # Fallback: Si intent es "author" pero no hay resultados, reintentar con threshold más bajo
    if intent == "author" and not matching_books:
        for book in books_data:
            author_score = fuzzy_score_author(query, book.author or "", threshold=60)
            if author_score >= 60:
                matching_books.append(book)

    if matching_books:
        ranked = rerank_books(matching_books, query)
        for i, book in enumerate(ranked[:10], 1):
            score = score_book(book, query)
            print(f'{i}. {book.title} | Autor: {book.author} | Score: {score}')
    else:
        print('   No se encontraron resultados')

    print()
