"""
Detector de intent de búsqueda.
Identifica si la query es para buscar por autor, título, ISBN, categoría, etc.
"""

import re
from typing import Literal

QueryIntent = Literal["author", "isbn", "title", "category", "mixed"]


def detect_query_intent(query: str) -> QueryIntent:
    """
    Detecta el tipo de búsqueda basado en el patrón de la query.

    Returns:
        - "author": Búsqueda por autor (ej: "José ZAPATA", "García Márquez")
        - "isbn": Búsqueda por ISBN (ej: "9788419087201")
        - "category": Búsqueda por categoría (ej: "novela", "filosofía")
        - "title": Búsqueda por título (ej: "el alquimista", "harry potter")
        - "mixed": Combinación de varios (query compleja)
    """
    query_normalized = query.lower().strip()

    # 1️⃣ Detectar ISBN (10 o 13 dígitos)
    if re.match(r'^\d{10}(?:\d{3})?$', query_normalized.replace('-', '').replace(' ', '')):
        return "isbn"

    # 2️⃣ Detectar patrón de autor
    words = query.split()
    word_count = len(words)

    # Palabras muy comunes en títulos (matching por palabra completa)
    title_words = {"el", "la", "los", "las", "de", "del", "y", "o", "en", "por", "con", "un", "una", "es", "son",
                   "historia", "guia", "manual", "libro", "coleccion", "enciclopedia"}

    if word_count <= 3:
        # Detectar si es probablemente nombre de autor

        # PATRÓN 1: Última palabra en MAYÚSCULA (típico de apellidos españoles)
        # "José ZAPATA", "Paulo COELHO", "García MÁRQUEZ"
        last_word = words[-1] if words else ""
        if len(last_word) > 2 and last_word.isupper():
            return "author"

        # Descartar si todas las palabras son palabras clave de título comunes
        has_title_keyword = any(w.lower() in title_words for w in words)

        if not has_title_keyword and word_count == 2:
            # PATRÓN para 2 palabras (caso más común de nombres de autores)
            # "Paulo Coelho", "García Márquez", "José Maria", "Isabella Allende"

            first_word = words[0]
            second_word = words[1]

            # PATRÓN especial: iniciales + apellido ("JK Rowling", "J K Rowling")
            is_initials = len(first_word) <= 3 and first_word.isalpha()
            if is_initials and len(second_word) >= 4:
                return "author"

            # Heurística 1: Primera palabra empieza con mayúscula O tiene acentos O tiene longitud nombre típica
            has_capital_or_accent_first = (len(first_word) > 0 and first_word[0].isupper()) or any(c in first_word for c in "áéíóúñü")
            is_typical_name_length_first = 3 <= len(first_word) <= 9  # Rango típico de nombres (Isabella, Paulo)

            # Heurística 2: Segunda palabra empieza con mayúscula O tiene acentos O es corta
            second_starts_capital = len(second_word) > 0 and second_word[0].isupper()
            has_name_chars_second = any(c in second_word for c in "áéíóúñüü")
            is_short = len(second_word) <= 6

            # Heurística 3: Longitud promedio (descartamos sustantivos formales largos)
            avg_length = (len(first_word) + len(second_word)) / 2

            # ADICIONAL: Descartar si ambas palabras son sustantivos formales
            # Sustantivos formales típicamente: Todos los caracteres después de la primera mayúscula son minúsculas
            # Y tienen longitud >= 7
            # "Gestion" (7), "Ambiental" (9) = sustantivos formales
            # "Paulo" (5), "Coelho" (6) = nombres propios (palabra corta)
            # "García" (6) = nombre propio (tiene acento)

            all_formal = True
            for w in [first_word, second_word]:
                # Un sustantivo formal típicamente:
                # - Empieza con mayúscula (capital initial)
                # - Es largo (>= 7 caracteres)
                # - Tiene solo minúsculas después de la mayúscula inicial
                # - NO tiene acentos ni mayúsculas internas
                # Ejemplos: "Gestion" (7), "Ambiental" (9)
                is_formal_noun = (w[0].isupper() if w else False) and len(w) >= 7
                if not is_formal_noun:
                    all_formal = False
                    break

            # Es autor si:
            # 1. (Primera palabra tiene capital O acentos O longitud típica de nombre) AND
            # 2. (Segunda palabra tiene capital OR acentos OR es corta) AND
            # 3. Promedio <= 8 caracteres AND
            # 4. NO es un patrón totalmente formal de sustantivos (ambas >= 7 chars)

            if all_formal:
                # Es un patrón formal como "Gestion Ambiental" (2 palabras formales largas) → es TÍTULO
                return "title"

            if (has_capital_or_accent_first or is_typical_name_length_first) and (second_starts_capital or has_name_chars_second or is_short) and avg_length <= 8:
                return "author"

        elif not has_title_keyword and word_count > 2:
            # PATRÓN para 3+ palabras: "Gabriel García Márquez"
            proper_word_count = 0
            for w in words:
                if (len(w) > 0 and w[0].isupper()) or any(c in w for c in "áéíóúñü"):
                    proper_word_count += 1

            # Si al menos 2 de 3 palabras parecen nombres propios
            if proper_word_count >= 2:
                return "author"

    # 3️⃣ Palabras clave de categoría
    category_keywords = {
        "novela", "poesía", "drama", "ficción", "ciencia ficción", "fantasy", "romance",
        "filosofía", "historia", "psicología", "sociología", "educación", "medicina",
        "biología", "química", "física", "matemáticas", "programación", "informática",
        "arte", "música", "deporte", "cocina", "viajes", "autoayuda", "negocio",
        "tecnología", "infantil", "juvenil", "religiós", "política", "economía"
    }

    if any(cat in query_normalized for cat in category_keywords):
        if word_count <= 3:
            return "category"
        else:
            return "mixed"

    # 4️⃣ Por defecto: título
    return "title"


def get_search_priority(intent: QueryIntent) -> dict[str, float]:
    """
    Retorna los pesos/prioridades para cada campo según el intent.
    """
    priorities = {
        "author": {
            "author": 1.0,
            "title": 0.2,
            "category": 0.1,
            "description": 0.05,
            "isbn": 0.0,
        },
        "isbn": {
            "isbn": 1.0,
            "author": 0.0,
            "title": 0.0,
            "category": 0.0,
            "description": 0.0,
        },
        "category": {
            "category": 1.0,
            "description": 0.8,
            "title": 0.3,
            "author": 0.1,
            "isbn": 0.0,
        },
        "title": {
            "title": 1.0,
            "description": 0.5,
            "author": 0.2,
            "category": 0.1,
            "isbn": 0.0,
        },
        "mixed": {
            "title": 0.8,
            "author": 0.6,
            "category": 0.5,
            "description": 0.4,
            "isbn": 0.0,
        },
    }

    return priorities.get(intent, priorities["title"])
