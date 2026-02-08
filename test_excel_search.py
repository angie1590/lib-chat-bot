#!/usr/bin/env python3
import sys
from pathlib import Path
import pandas as pd

# Agregar src/ al path para importar lib_chat_bot
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from lib_chat_bot.catalog.search_engine import score_book, rerank_books
from lib_chat_bot.catalog.models import Book

# Leer la base de datos de Excel
df = pd.read_excel(project_root / 'SDLLista14nov2025.xlsx')

# Convertir a objetos Book
books_data = []
for idx, row in df.iterrows():
    # Crear un ID numérico desde el string
    id_str = str(row['Cod. Item'])
    numeric_id = abs(hash(id_str)) % (10 ** 9)

    # Manejar valores NaN
    title = row['TITULO'] if pd.notna(row['TITULO']) else ""
    author = row['AUTOR'] if pd.notna(row['AUTOR']) else None
    publisher = row['EDITORIAL'] if pd.notna(row['EDITORIAL']) else None

    if not title:  # Skip si no hay título
        continue

    book = Book(
        id=numeric_id,
        title=str(title),
        author=str(author) if author else None,
        publisher=str(publisher) if publisher else None,
        stock=int(row['Existencia']) if pd.notna(row['Existencia']) else 0,
    )
    books_data.append(book)

print(f"Cargados {len(books_data)} libros de la base de datos\n")

# Pruebas de búsqueda
test_queries = [
    "el alquimista",
    "el alqimsta",  # typo
    "harry potter 1",
    "quimica",  # Debe devolver libros reales de química, no "alquimista"
    "python programacion",
    "inteligencia artificial",
    "economia",
    "novela romantica",
]

for query in test_queries:
    print("=" * 80)
    print(f"Consulta: {query}")
    print("=" * 80)

    # Buscar libros que contengan palabras clave de la query (búsqueda simple)
    query_words = set(query.lower().split())
    matching_books = []

    for book in books_data:
        title_lower = (book.title or "").lower()
        author_lower = (book.author or "").lower()

        # Si hay alguna palabra clave en el título o autor
        for word in query_words:
            if len(word) > 2 and (word in title_lower or word in author_lower):
                matching_books.append(book)
                break

    # Puntuar y ordenar
    if matching_books:
        scored = [(score_book(b, query), b) for b in matching_books]
        scored.sort(key=lambda x: x[0], reverse=True)

        # Mostrar top 5
        for i, (score, book) in enumerate(scored[:5], 1):
            print(f"{i}. {book.title} | Autor: {book.author} | Score: {score}")
    else:
        print("   No se encontraron resultados")

    print()
