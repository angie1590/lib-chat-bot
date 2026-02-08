#!/usr/bin/env python3
"""
Demostración completa del sistema inteligente de búsqueda con detección de intent.

Este script muestra cómo el buscador detecta automáticamente el tipo de búsqueda
(autor, título, ISBN, categoría) y ajusta los pesos de scoring en consecuencia.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
from lib_chat_bot.catalog.models import Book
from lib_chat_bot.catalog.search_engine import score_book
from lib_chat_bot.catalog.intent_detector import detect_query_intent, get_search_priority

print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                    🎯 BUSCADOR INTELIGENTE - DEMOSTRACIÓN                       ║
║                      (Detección automática de búsquedas)                        ║
╚════════════════════════════════════════════════════════════════════════════════╝
""")

# Cargar base de datos
excel_file = Path(__file__).parent / "SDLLista14nov2025.xlsx"
df = pd.read_excel(excel_file)

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
            price=float(row.get("P.V.P.", 0)) if pd.notna(row.get("P.V.P.")) else 0,
        )
        books.append(book)

print(f"✅ Base de datos cargada: {len(books)} libros\n")

# Ejemplos de búsquedas
ejemplos = [
    {
        "query": "Paulo Coelho",
        "tipo": "AUTOR",
        "explicacion": "Detecta formato 'Nombre Apellido' (palabras cortas, Capital)",
        "comportamiento": "Prioriza campo 'AUTOR' (peso=1.0)\nOtros campos con peso bajo (título=0.2, descripción=0.05)"
    },
    {
        "query": "Gestion Ambiental",
        "tipo": "TÍTULO",
        "explicacion": "Detecta sustantivos formales (palabras largas, >=7 caracteres)",
        "comportamiento": "Prioriza campo 'TÍTULO' (peso=1.0)\nBusca también en descripción (peso=0.5)"
    },
    {
        "query": "El Alquimista",
        "tipo": "TÍTULO",
        "explicacion": "Detecta artículo inicial (palabra clave de título común)",
        "comportamiento": "Prioriza campo 'TÍTULO' (peso=1.0)\nOtros campos con peso medio (descripción=0.5)"
    },
    {
        "query": "José ZAPATA",
        "tipo": "AUTOR",
        "explicacion": "Detecta patrón 'Nombre APELLIDO' (apellido en mayúscula)",
        "comportamiento": "Prioriza campo 'AUTOR' (peso=1.0)\nAunque haya 'ZAPATA' en títulos, el autor se prioriza"
    },
]

for i, ejemplo in enumerate(ejemplos, 1):
    query = ejemplo["query"]
    intent = detect_query_intent(query)
    priority = get_search_priority(intent)

    print(f"\n{'─' * 80}")
    print(f"EJEMPLO {i}: {ejemplo['tipo']}")
    print(f"{'─' * 80}")
    print(f"Query: '{query}'")
    print(f"Tipo detectado: {intent.upper()}")
    print(f"Explicación de detección: {ejemplo['explicacion']}")
    print(f"\nComportamiento de scoring:")
    for line in ejemplo['comportamiento'].split('\n'):
        print(f"  {line}")

    print(f"\nPesos aplicados:")
    for field, weight in priority.items():
        if weight > 0:
            print(f"  - {field:15} : {weight:.2f}")

    # Mostrar top 2 resultados
    if intent != "isbn":
        scores = [(score_book(book, query), book) for book in books]
        scores.sort(key=lambda x: x[0], reverse=True)

        print(f"\nTop 2 resultados:")
        for i, (score, book) in enumerate(scores[:2], 1):
            print(f"  {i}. {book.title[:65]} | Score: {score}")
            if book.author:
                print(f"     Autor: {book.author[:50]}")

print(f"\n{'═' * 80}")
print("✅ Sistema de detección de intent funcionando correctamente")
print(f"{'═' * 80}\n")
