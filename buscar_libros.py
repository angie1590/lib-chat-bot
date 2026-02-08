#!/usr/bin/env python3
"""
Script interactivo para buscar libros en la catálogo.
Permite escribir queries y devuelve los 10 resultados más relevantes.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from lib_chat_bot.catalog.models import Book
from lib_chat_bot.catalog.search_engine import score_book, fuzzy_score_author, fuzzy_score_title, rerank_books
from lib_chat_bot.catalog.intent_detector import detect_query_intent
import re


def normalize_query(query: str) -> str:
    """Extrae solo el nombre del autor de queries conversacionales."""
    # Patrones como "libros de García Márquez" → "García Márquez"
    match = re.search(r'\b(libros|obras|libreta|escritos)\s+(de|por|del|con)\s+(.+?)(?:\s+de\s+|$)', query, re.IGNORECASE)
    if match:
        author = match.group(3).strip()
        for word in ['que', 'donde', 'cuando', 'porque', 'para']:
            if author.endswith(word):
                author = author[:-len(word)].strip()
        return author
    
    # Patrón alternativo: palabras mayúsculas después de "de" o "por"
    match = re.search(r'\b(?:de|por|del|about)\s+([A-ZÁÉÍÓÚ][a-záéíóú]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóú]+)*)', query)
    if match:
        author = match.group(1).strip()
        if any(c.isupper() for c in author):
            return author
    
    return query


def load_books():
    """Carga los libros del Excel una sola vez."""
    print("📚 Cargando catálogo de libros...", end=" ", flush=True)
    
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
    
    print(f"✅ {len(books_data)} libros cargados")
    return books_data


def search_books(query: str, books_data: list) -> list:
    """Ejecuta la búsqueda y devuelve los libros encontrados."""
    # Normalizar query si es conversacional
    normalized_query = normalize_query(query)
    if normalized_query != query:
        print(f"  (Búsqueda: {normalized_query})")
    
    intent = detect_query_intent(normalized_query)
    query_words = set(normalized_query.lower().split())
    matching_books = []

    for book in books_data:
        title_lower = (book.title or '').lower()
        author_lower = (book.author or '').lower()
        isbn_clean = (book.isbn or '').replace('-', '').replace(' ', '')

        if intent == "isbn":
            # ISBN search: exact match only
            query_clean = normalized_query.replace('-', '').replace(' ', '')
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

    return matching_books


def display_results(matching_books: list, query: str, max_results: int = 10):
    """Muestra los resultados de la búsqueda."""
    if not matching_books:
        print("\n❌ No se encontraron resultados")
        return

    ranked = rerank_books(matching_books, query)
    total = len(ranked)
    display_count = min(max_results, total)
    
    print(f"\n✅ Encontrados {total} libro(s) - Mostrando {display_count}:")
    print("=" * 100)
    
    for i, book in enumerate(ranked[:display_count], 1):
        score = score_book(book, query)
        author_str = book.author if book.author else "Desconocido"
        print(f"{i:2}. {book.title[:65]:65} | {author_str[:28]:28} | {score:6.0f}")
    
    print("=" * 100)


def main():
    """Función principal del script interactivo."""
    print("\n" + "=" * 100)
    print("🔍 BUSCADOR DE LIBROS - Catálogo Interactivo".center(100))
    print("=" * 100 + "\n")
    
    # Cargar libros una sola vez
    books_data = load_books()
    print()
    
    while True:
        # Pedir query al usuario
        print("\n📖 Ingrese su búsqueda (autor, título, ISBN, etc.):")
        print("   (escriba 'salir' para terminar)")
        query = input("\n> ").strip()
        
        if query.lower() in ['salir', 'exit', 'quit', 'q']:
            print("\n👋 ¡Hasta luego!")
            break
        
        if not query:
            print("⚠️  Por favor, ingrese una búsqueda válida")
            continue
        
        # Ejecutar búsqueda
        print(f"\n🔎 Buscando: '{query}'")
        matching_books = search_books(query, books_data)
        
        # Mostrar resultados
        display_results(matching_books, query)
        
        # Preguntar si quiere hacer otra búsqueda
        while True:
            print("\n¿Desea realizar otra búsqueda? (s/n): ", end="")
            response = input().strip().lower()
            if response in ['s', 'si', 'sí', 'yes', 'y']:
                break
            elif response in ['n', 'no']:
                print("\n👋 ¡Hasta luego!")
                return
            else:
                print("⚠️  Por favor, ingrese 's' o 'n'")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Búsqueda interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
