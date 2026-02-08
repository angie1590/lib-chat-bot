#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from lib_chat_bot.catalog.models import Book
from lib_chat_bot.catalog.search_engine import score_book, fuzzy_score_author, fuzzy_score_title, rerank_books
from lib_chat_bot.catalog.intent_detector import detect_query_intent
import re

# Función para extraer autor de queries conversacionales
def normalize_query(query: str) -> str:
    """Extrae solo el nombre del autor de queries conversacionales."""
    # Patrones como "libros de García Márquez" → "García Márquez"
    match = re.search(r'\b(libros|obras|libreta|escritos)\s+(de|por|del|del|con)\s+(.+?)(?:\s+de\s+|$)', query, re.IGNORECASE)
    if match:
        author = match.group(3).strip()
        # Limpiar palabras comunes al final
        for word in ['que', 'donde', 'cuando', 'porque', 'para']:
            if author.endswith(word):
                author = author[:-len(word)].strip()
        return author
    
    # Patrón alternativo: palabras mayúsculas después de "de" o "por" (García Márquez)
    # Útil para "quiero libros que hablen de García Márquez"
    match = re.search(r'\b(?:de|por|del|about)\s+([A-ZÁÉÍÓÚ][a-záéíóú]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóú]+)*)', query)
    if match:
        author = match.group(1).strip()
        # Solo retornar si tiene mayúsculas (es un nombre propio)
        if any(c.isupper() for c in author):
            return author
    
    return query

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
    '9786287641969',
    '9786287641890',
    'Ensayos breves para la relijion',
    'FUCOL, MICHEL',
    'libros de García Márquez',  # Query conversacional
    'quiero libros que hablen de García Márquez',  # Query natural
    'jarry poter 1',  # Harry Potter con typo
]

for query in test_queries:
    print('=' * 80)
    print(f'Consulta: {query}')
    print('=' * 80)

    # Normalizar query si es necesaria
    normalized_query = normalize_query(query)
    if normalized_query != query:
        print(f'  (Normalizada a: {normalized_query})')
        print()
    
    intent = detect_query_intent(normalized_query)
    query_words = set(normalized_query.lower().split())
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
            author_score = fuzzy_score_author(normalized_query, book.author or "", threshold=75)
            if author_score >= 75:
                matching_books.append(book)
        else:
            # Title search: first try exact words, then fuzzy matching
            exact_match = False
            for word in query_words:
                if len(word) > 2 and (word in title_lower or word in author_lower):
                    matching_books.append(book)
                    exact_match = True
                    break
            
            # Fallback: fuzzy match on title if no exact word match
            if not exact_match:
                title_score = fuzzy_score_title(normalized_query, book.title or "", threshold=70)
                if title_score >= 70:
                    matching_books.append(book)

    # Fallback: Si intent es "author" pero no hay resultados, reintentar con threshold más bajo
    if intent == "author" and not matching_books:
        for book in books_data:
            author_score = fuzzy_score_author(normalized_query, book.author or "", threshold=60)
            if author_score >= 60:
                matching_books.append(book)

    if matching_books:
        ranked = rerank_books(matching_books, normalized_query)
        for i, book in enumerate(ranked[:10], 1):
            score = score_book(book, query)
            print(f'{i}. {book.title} | Autor: {book.author} | Score: {score}')
    else:
        print('   No se encontraron resultados')

    print()
