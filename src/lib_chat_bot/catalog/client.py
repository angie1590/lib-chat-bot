import os
import httpx
import logging
from typing import List
from functools import lru_cache

from .models import Book
from .search_engine import rerank_books
from .synonyms import TITLE_ALIASES
from .fallback import (
    simplify_query,
    extract_keywords,
    extract_series_numbers,
    generate_prefixes,
    correct_query_typos,
)

# Configurar logging
logger = logging.getLogger(__name__)

BASE_URL = "https://www.sodilibro.com:8000/api/shopcart/vwitemTienda/"

# ⚠️ Certificado SSL inválido en entorno SODILIBRO
VERIFY_SSL = os.getenv("SODILIBRO_VERIFY_SSL", "false").lower() == "true"

# Caché de búsquedas en memoria
_search_cache: dict[str, List[Book]] = {}


def _call_api(query: str, limit: int = 20) -> List[Book]:
    """Llamada directa a la API de SODILIBRO"""
    params = [
        ("opcion", "dynamic"),
        ("limit", str(limit)),
        ("offset", "0"),
        ("search", ""),
        ("search", query),
    ]

    response = httpx.get(
        BASE_URL,
        params=params,
        timeout=15,
        verify=VERIFY_SSL,
    )
    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])

    books: List[Book] = []

    for item in results:
        books.append(
            Book(
                id=item["id"],
                title=item.get("title"),
                author=item.get("desc2"),
                publisher=item.get("desc3"),
                category=item.get("desc4"),
                subcategory=item.get("desc5"),
                price=item.get("price") or item.get("precio1"),
                stock=item.get("stock"),
                isbn=item.get("codalterno1"),
                description=item.get("descripcion"),
            )
        )

    return books


def search_books(query: str, limit: int = 20) -> List[Book]:
    """
    Búsqueda robusta con fallback y caché:
    0) Revisar caché
    0.5) Intentar alias de títulos conocidos (ej: "harry potter 1" -> "piedra filosofal 1")
    1) Corregir typos y reintentar
    2) query original
    3) query simplificada
    4) keywords + números de serie
    5) prefijos
    """

    # 0️⃣ Revisar caché
    cache_key = f"{query}:{limit}"
    if cache_key in _search_cache:
        logger.debug(f"📦 Resultado obtenido del caché para: {query}")
        return _search_cache[cache_key]

    # 0.5️⃣ Intentar alias de títulos conocidos
    query_normalized = query.lower().strip()
    if query_normalized in TITLE_ALIASES:
        logger.debug(f"🎯 Usando alias para query: {query}")
        all_books = []
        # Para cada alias, pedir resultados
        # Los primeros alias (más específicos) piden más para asegurar diversidad
        for i, alias_query in enumerate(TITLE_ALIASES[query_normalized]):
            # Primer alias: pedir más; siguientes: pedir menos para llenar
            api_limit = limit if i == 0 else (limit // 2)
            logger.debug(f"🔍 Buscando con alias ({i+1}): {alias_query} (limit={api_limit})")
            books = _call_api(alias_query, api_limit)
            if books:
                all_books.extend(books)

        if all_books and len(all_books) >= 5:  # Solo retornar si hay suficientes resultados
            # Eliminar duplicados por ID, preservando el orden original
            seen_ids = set()
            unique_books = []
            for book in all_books:
                if book.id not in seen_ids:
                    unique_books.append(book)
                    seen_ids.add(book.id)

            result = unique_books[:limit]
            _search_cache[cache_key] = result
            logger.info(f"✅ Encontrados {len(result)} libros únicos con alias")
            # Reranquear todos los resultados combinados por relevancia a la query original
            return rerank_books(result, query)

        # Si hay menos de 5 resultados, continuar con fallback para completar
        if all_books:
            logger.debug(f"⚠️ Alias devolvió pocos resultados ({len(all_books)}), continuando con fallback...")

    # 1️⃣ Intento directo
    logger.debug(f"🔍 Buscando: {query}")
    books = _call_api(query, limit)
    if books:
        _search_cache[cache_key] = books
        logger.info(f"✅ Encontrados {len(books)} libros con query directa")
        return rerank_books(books, query)

    # 1.5️⃣ Corregir typos y reintentar
    corrected = correct_query_typos(query)
    if corrected != query:
        logger.debug(f"🔧 Query corregida: {query} → {corrected}")
        books_corrected = _call_api(corrected, limit)

        # Si hay libros del alias previo, combinarlos con los corregidos
        alias_ids_set = set()
        if 'all_books' in locals() and all_books:
            alias_ids_set = {book.id for book in all_books}
            all_books.extend(books_corrected)
            seen_ids = set()
            unique_books = []
            for book in all_books:
                if book.id not in seen_ids:
                    unique_books.append(book)
                    seen_ids.add(book.id)
            result = unique_books[:limit]
            _search_cache[cache_key] = result
            logger.info(f"✅ Encontrados {len(result)} libros combinando alias + corrección de typos")
            # Reranquear preservando los libros del alias en posiciones altas
            return rerank_books(result, query, boost_ids=alias_ids_set)
        elif books_corrected:
            cache_key_corrected = f"{corrected}:{limit}"
            _search_cache[cache_key] = books_corrected
            _search_cache[cache_key_corrected] = books_corrected
            logger.info(f"✅ Encontrados {len(books_corrected)} libros con query corregida")
            return rerank_books(books_corrected, query)

    # 2️⃣ Query simplificada
    simplified = simplify_query(query)
    if simplified and simplified != query:
        logger.debug(f"🔄 Intentando query simplificada: {simplified}")
        books = _call_api(simplified, limit)
        if books:
            _search_cache[cache_key] = books
            logger.info(f"✅ Encontrados {len(books)} libros con query simplificada")
            return rerank_books(books, query)

    # 3️⃣ Keywords + Números de serie + prefijos
    keywords = extract_keywords(query)
    series_numbers = extract_series_numbers(query)

    logger.debug(f"🔑 Keywords extraídas: {keywords}")
    logger.debug(f"🔢 Números de serie: {series_numbers}")

    # Si hay números de serie, intentar combinaciones con keywords
    all_books = []
    if series_numbers:
        for number in series_numbers:
            for keyword in keywords:
                combined_query = f"{keyword} {number}"
                logger.debug(f"🔍 Buscando combinación: {combined_query}")
                books = _call_api(combined_query, limit)
                if books:
                    all_books.extend(books)

        # Si encontramos libros con las combinaciones, devolver todos rerankeados
        if all_books:
            # Eliminar duplicados por ID
            unique_books = {book.id: book for book in all_books}.values()
            result = list(unique_books)[:limit]
            _search_cache[cache_key] = result
            logger.info(f"✅ Encontrados {len(result)} libros únicos con combinaciones")
            return rerank_books(result, query)

    # Búsqueda por keywords simples
    for keyword in keywords:
        # intento keyword directa
        logger.debug(f"🔍 Buscando keyword: {keyword}")
        books = _call_api(keyword, limit)
        if books:
            _search_cache[cache_key] = books
            logger.info(f"✅ Encontrados {len(books)} libros con keyword: {keyword}")
            return rerank_books(books, query)

        # 🔥 prefijos
        for prefix in generate_prefixes(keyword):
            logger.debug(f"🔍 Buscando prefijo: {prefix}")
            books = _call_api(prefix, limit)
            if books:
                _search_cache[cache_key] = books
                logger.info(f"✅ Encontrados {len(books)} libros con prefijo: {prefix}")
                return rerank_books(books, query)

    # ❌ No se encontró nada
    logger.warning(f"⚠️ No se encontraron libros para: {query}")
    return []