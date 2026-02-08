from typing import List
from .search_engine import normalize
from Levenshtein import distance as levenshtein_distance

STOPWORDS = {
    "el", "la", "los", "las",
    "un", "una",
    "de", "del",
    "autor",
    "libro", "libros",
    "busco", "quiero", "necesito",
}

# Diccionario de palabras comunes en nuestro catálogo
COMMON_WORDS = {
    "gestion", "ambiental", "empresa", "calidad", "competitividad",
    "medio", "ambiente", "residuos", "sostenible", "turismo",
    "auditoria", "financiero", "desarrollo", "implementacion",
    "fundamentos", "lineamientos", "comunicacion", "sustentabilidad",
    "paulo", "coelho", "alquimista", "alquimia", "poder",
    "harry", "potter", "piedra", "filosofal", "hogwarts", "magia",
    # Añadir variaciones comunes de autores y títulos populares
    "rowling", "hermione", "ron", "voldemort", "dumbledore",
}


def correct_typo(word: str, candidates: set[str] = None) -> str:
    """
    Corrige typos usando distancia Levenshtein.
    Si encuentra una palabra muy similar, la retorna.
    Prioriza palabras más largas (títulos de libros suelen ser específicos).

    Ejemplo:
        correct_typo("anbiental") -> "ambiental"
        correct_typo("enpresa") -> "empresa"
        correct_typo("poter") -> "potter"
    """
    if candidates is None:
        candidates = COMMON_WORDS

    if word in candidates:
        return word

    # Calcular similitud con todas las palabras candidatas
    matches = []  # Lista de (distancia, palabra_length, palabra)

    for candidate in candidates:
        # Permitir diferencia de hasta 3 caracteres (para "poter" → "potter")
        len_diff = abs(len(word) - len(candidate))
        if len_diff > 3:
            continue

        distance = levenshtein_distance(word, candidate)

        # Si la distancia es pequeña relativa al tamaño, es un typo probable
        if distance < len(word) * 0.4:
            matches.append((distance, len(candidate), candidate))

    if matches:
        # Ordenar por: distancia (menor mejor), luego por longitud (mayor mejor = más específico)
        matches.sort(key=lambda x: (x[0], -x[1]))
        return matches[0][2]

    return word


def correct_query_typos(query: str) -> str:
    """
    Corrige typos en toda la query.

    Ejemplo:
        correct_query_typos("gestion anbiental en la enpresa")
        -> "gestion ambiental en la empresa"
    """
    words = normalize(query).split()
    corrected = [correct_typo(w) if len(w) >= 4 else w for w in words]
    return " ".join(corrected)


def simplify_query(query: str) -> str:
    words = normalize(query).split()
    return " ".join(w for w in words if w not in STOPWORDS)


def extract_keywords(query: str) -> List[str]:
    words = simplify_query(query).split()
    keywords = [w for w in words if len(w) >= 4]

    # Agregar palabras adicionales que podrían ser relevantes pero fueron filtradas
    # Por ejemplo, "piedra" es importante en "Harry Potter y la piedra filosofal"
    # Incluso si fue eliminada por stopwords
    original_words = query.lower().split()
    for word in original_words:
        if len(word) >= 5 and word not in keywords and word not in STOPWORDS:
            keywords.append(word)

    return keywords


def extract_series_numbers(query: str) -> List[str]:
    """
    Extrae números de la query (para búsquedas de series como 'harry potter 1')
    Ejemplo:
        extract_series_numbers("harry potter 1") -> ["1"]
        extract_series_numbers("harry 2 potter") -> ["2"]
    """
    import re
    numbers = re.findall(r'\d+', query)
    return numbers


def generate_prefixes(word: str, min_len: int = 4) -> List[str]:
    """
    Genera prefijos decrecientes:
    alquimista -> alqui, alqu, alqi (según longitud)
    """
    prefixes = []
    for i in range(len(word), min_len - 1, -1):
        prefixes.append(word[:i])
    return prefixes