#!/usr/bin/env python3
"""
Test para demostrar el sistema de detección de intent
y cómo afecta el scoring de resultados.
"""

import sys
import pandas as pd
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lib_chat_bot.catalog.models import Book
from lib_chat_bot.catalog.search_engine import score_book
from lib_chat_bot.catalog.intent_detector import detect_query_intent, get_search_priority

def test_intent_detection():
    """Prueba el sistema de detección de intents con ejemplos del mundo real."""

    # Cargar base de datos de libros
    excel_file = Path(__file__).parent / "SDLLista14nov2025.xlsx"
    df = pd.read_excel(excel_file)

    books = []
    for idx, row in df.iterrows():
        if pd.notna(row.get("TITULO")):
            # Convertir ID de forma segura
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
                price=float(row.get("P.V.P.", 0)) if pd.notna(row.get("P.V.P.")) else 0,
            )
            books.append(book)

    print(f"✅ Cargados {len(books)} libros de la base de datos\n")

    # Test queries con diferentes intents
    test_cases = [
        # Búsquedas por AUTOR
        {
            "query": "José ZAPATA",
            "expected_intent": "author",
            "description": "Nombre de autor (Nombre APELLIDO)"
        },
        {
            "query": "García maquez",
            "expected_intent": "author",
            "description": "Nombre de autor (apellido con variación)"
        },
        {
            "query": "Paulo Coelho",
            "expected_intent": "author",
            "description": "Nombre de autor conocido"
        },
        # Búsquedas por TÍTULO
        {
            "query": "Gestion Ambiental",
            "expected_intent": "title",
            "description": "Término descriptivo (no nombre propio)"
        },
        {
            "query": "el alquimista",
            "expected_intent": "title",
            "description": "Título de libro"
        },
        {
            "query": "harry potter piedra filosofal",
            "expected_intent": "title",
            "description": "Título descriptivo"
        },
        # Búsquedas por ISBN
        {
            "query": "978-84-1234567890",
            "expected_intent": "isbn",
            "description": "ISBN válido (13 dígitos)"
        },
        {
            "query": "8412345678",
            "expected_intent": "isbn",
            "description": "ISBN válido (10 dígitos)"
        },
        # Búsquedas por CATEGORÍA
        {
            "query": "novela fiction",
            "expected_intent": "category",
            "description": "Término de categoría"
        },
        {
            "query": "filosofía",
            "expected_intent": "category",
            "description": "Área de conocimiento"
        },
    ]

    print("=" * 80)
    print("PRUEBA DE DETECCIÓN DE INTENT Y IMPACTO EN SCORING")
    print("=" * 80)

    for test_case in test_cases:
        query = test_case["query"]
        expected_intent = test_case["expected_intent"]
        description = test_case["description"]

        # Detectar intent
        detected_intent = detect_query_intent(query)
        priority = get_search_priority(detected_intent)

        # Mostrar resultado de detección
        status = "✅" if detected_intent == expected_intent else "❌"
        print(f"\n{status} QUERY: '{query}'")
        print(f"   Descripción: {description}")
        print(f"   Intent detectado: {detected_intent} (esperado: {expected_intent})")
        print(f"   Prioridades: {priority}")

        # Ejecutar búsqueda solo si la query es válida
        if len(query.strip()) >= 2 and detected_intent != "isbn":
            # Scoring de todos los libros
            scores = [(score_book(book, query), book) for book in books]
            scores.sort(key=lambda x: x[0], reverse=True)
            results = scores[:3]
            if results:
                print(f"   🔍 Top 3 resultados:")
                for i, (score, book) in enumerate(results, 1):
                    print(f"      {i}. {book.title[:60]} | Score: {score}")

    print("\n" + "=" * 80)
    print("IMPACTO DE INTENTS EN SCORING")
    print("=" * 80)
    print("""
Ejemplo: Búsqueda "José ZAPATA"
- SIN intents: Buscaría en todos los campos por igual
- CON intents: Prioriza author=1.0, title=0.2, description=0.1

Resultado: Libros CON "ZAPATA" en autor tienen mucho mayor score
que libros que solo mencionan "ZAPATA" en el título.

Esto permite:
✅ Autor "ZAPATA" = Top 1
✅ Evita títulos irrelevantes que contengan "ZAPATA" incidentalmente
✅ Mantiene "García Márquez" al buscar "García maquez" (fuzzy matching)
""")

if __name__ == "__main__":
    test_intent_detection()
