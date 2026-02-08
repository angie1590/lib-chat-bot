from typing import List, Tuple, Optional
from rapidfuzz.fuzz import ratio, partial_ratio, token_sort_ratio
from Levenshtein import distance as levenshtein_distance

from .models import Book
from .synonyms import expand_query_with_synonyms, normalize_with_synonyms
from .intent_detector import detect_query_intent, get_search_priority


def normalize(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
    }

    text = text.lower().strip()
    for k, v in replacements.items():
        text = text.replace(k, v)

    # Eliminar puntuación común (comas, puntos)
    for punct in [",", ".", ";", ":"]:
        text = text.replace(punct, " ")

    return text


def extract_title_and_author(query: str) -> Tuple[str, Optional[str]]:
    q = normalize(query)

    if "autor" in q:
        parts = q.split("autor", 1)
        return parts[0].strip(), parts[1].strip()

    return q, None


def fuzzy_score_author(query: str, author: str, threshold: float = 75) -> int:
    """
    Fuzzy score especializado para búsquedas de autor.
    Prioriza coincidencias de múltiples palabras (apellidos).

    Args:
        query: Query del usuario
        author: Nombre del autor
        threshold: Threshold de fuzzy matching por palabra (default 75, puede bajarse a 60-65 para typos grandes)
    """
    if not query or not author:
        return 0

    query_norm = normalize(query)
    author_norm = normalize(author)

    query_words = [w for w in query_norm.split() if len(w) > 2]
    author_words = [w for w in author_norm.split() if len(w) > 2]

    if not query_words or not author_words:
        return 0

    query_word_count = len(query_words)
    exact_match_count = sum(1 for qw in query_words if qw in author_words)

    # Coincidencia exacta de todas las palabras
    if exact_match_count == query_word_count:
        return 98

    # Fuzzy por palabra: mejor match por cada palabra de la query
    matched_count = 0
    total_score = 0
    matched_words = set()
    for qw in query_words:
        best = 0
        for aw in author_words:
            score = ratio(qw, aw)
            if score > best:
                best = score
        if best >= threshold:
            matched_count += 1
            total_score += best
            matched_words.add(qw)

    if query_word_count == 1:
        return int(total_score) if matched_count == 1 else 0

    # Si la query tiene 2+ palabras, exigir TODAS salvo que la(s) no coincidentes
    # parezcan nombres propios comunes o iniciales.
    if matched_count == query_word_count:
        avg_score = total_score / matched_count
        return int(avg_score)

    unmatched_words = [w for w in query_words if w not in matched_words]
    common_given_names = {
        "jose", "juan", "maria", "luis", "ana", "carlos", "jorge",
        "marta", "lucia", "pedro", "miguel", "angel", "andres",
        "silvia", "paula", "paul", "gabriel", "julia", "sara",
        "isabella", "isabel", "jose", "jaime", "carlos", "diego",
        "francisco", "fernando", "manuel", "rafael", "alejandro",
    }
    if matched_count >= 1 and unmatched_words:
        if all(len(w) <= 3 or w in common_given_names for w in unmatched_words):
            avg_score = total_score / matched_count
            return int(avg_score * 0.9)

    return 0


def fuzzy_score(a: str, b: str) -> int:
    if not a or not b:
        return 0

    # Calcular distancia Levenshtein para detectar typos
    # Normalizar primero
    a_norm = normalize(a)
    b_norm = normalize(b)

    # ⚠️ NO comparar palabras que tengan muy diferente longitud
    # Esto evita que "alquimista" matchee con "quimica"
    len_ratio = min(len(a_norm), len(b_norm)) / max(len(a_norm), len(b_norm))
    if len_ratio < 0.6:  # Si una palabra es < 60% del tamaño de la otra, no son similares
        return 0

    # Si son muy similares en distancia, dar bonus
    if len(a_norm) > 3 and len(b_norm) > 3:
        lev_dist = levenshtein_distance(a_norm, b_norm)
        max_len = max(len(a_norm), len(b_norm))
        # Si la distancia es pequeña relativa al tamaño, dar bonus
        if lev_dist <= max_len * 0.3:  # Tolerancia del 30%
            return 85  # Score alto para typos detectados

    # Sino usar fuzzy matching tradicional
    # Pero respetar la restricción de longitud
    return max(
        ratio(a, b),
        partial_ratio(a, b),
        token_sort_ratio(a, b),
    )


def score_book(book: Book, query: str) -> int:
    # Detectar intent de la búsqueda PRIMERO
    intent = detect_query_intent(query)
    priority = get_search_priority(intent)

    # Si es búsqueda de autor, usar toda la query como autor
    if intent == "author":
        title_q = None
        author_q = query
    else:
        title_q, author_q = extract_title_and_author(query)

    # Normalizar primero
    normalized_query = normalize(query)

    title = normalize(book.title or "")
    author = normalize(book.author or "")
    publisher = normalize(book.publisher or "")
    category = normalize(book.category or "")
    description = normalize(book.description or "")

    score = 0

    # Preparar palabras para análisis
    original_words = set(normalized_query.split())
    title_words = set(title.split())
    original_unique_words = [w for w in original_words if len(w) > 3 and w not in {"harry", "potter", "piedra", "filosofal"}]


    # 🔢 PRIMERO: Bonus crítico para números en serie (Harry Potter 1, 2, 3, etc.)
    # Pero SOLO si el typo/palabra no es la palabra dominante de la query
    # Si hay typos como "jarry" o "poter", esos typos tienen más peso que el número
    import re
    query_numbers = set(re.findall(r'\d+', normalized_query))
    title_numbers = set(re.findall(r'\d+', title))

    # Si la query tiene palabras únicas (typos), la prioridad es la coincidencia del typo, no del número
    has_unique_words = any(original_unique_words)

    series_match_bonus = 0
    if query_numbers and not has_unique_words:  # Solo si NO hay typos en la query
        if title_numbers:
            # Si coinciden los números, dar BONUS
            if query_numbers & title_numbers:
                series_match_bonus = 200  # Bonus crítico para coincidencia de números
            else:
                # Si hay números pero no coinciden, penalizar
                series_match_bonus = -100  # Penalización para números que no coinciden
        else:
            # Si la query tiene números pero el título no, penalizar levemente
            series_match_bonus = -30  # Penalización leve para libros sin números
    elif query_numbers and title_numbers and (query_numbers & title_numbers):
        # Si hay typos pero el número coincide, dar bonus menor
        series_match_bonus = 80  # Bonus menor si hay typos pero el número coincide

    score += series_match_bonus

    # 🔤 Bonus por coincidencia parcial de palabras clave originales (para typos severos)
    # Si la query tiene palabras únicas como "jarry" que no sean comunes, dar bonus si están similares en el título
    if original_unique_words:  # Si hay palabras únicas/typos en la query
        for orig_word in original_unique_words:
            for title_word in title_words:
                if len(title_word) > 3:
                    # Búsqueda 1: Distancia Levenshtein directa (palabras similares)
                    lev_dist = levenshtein_distance(orig_word, title_word)
                    if lev_dist <= max(1, len(orig_word) * 0.3):
                        score += 250
                    # Búsqueda 2: Substring fuzzy (palabra dentro de palabra con pequeña distancia)
                    # Ej: "poter" dentro de "jarripoter"
                    elif orig_word in title_word:
                        score += 200
                    elif any(orig_word[i:i+4] in title_word for i in range(len(orig_word)-3)):
                        # Buscar substrings de 4+ caracteres del typo dentro del título
                        score += 150

    # 🎯 SCORING POR CAMPOS según intent detectado

    # Autor - dar MUCHO mayor peso si intent es "author"
    author_match_author = fuzzy_score_author(normalized_query, author)
    if intent == "author":
        # Para búsqueda de autor, usar fuzzy_score_author (compara palabras clave)
        author_match = author_match_author
    else:
        # Para búsquedas normales, usar fuzzy_score estándar
        author_match = fuzzy_score(normalized_query, author)

    if intent == "author":
        # BÚSQUEDA SELECTIVA: Si el autor NO coincide bien, penalizar SEVERAMENTE
        if author_match < 50:
            # El autor no coincide lo suficiente
            # Para búsquedas de autor, solo queremos resultados donde REALMENTE coincida el autor
            score -= 1000  # Penalización SEVERA para autores que no coinciden
        else:
            # El autor sí coincide bien - BOOST MÁXIMO
            score += int(author_match * 8.0 * priority["author"])
    else:
        score += int(author_match * 2.5 * priority["author"])
        # Bonus extra si el autor coincide fuerte aunque el intent sea título
        if author_match_author >= 80:
            score += int(author_match_author * 1.5)

    # Título
    title_match = fuzzy_score(normalized_query, title)

    # Si intent es "author", IGNORAR completamente el título para scoring
    # No buscamos por título cuando el usuario busca por autor
    if intent == "author":
        # Para búsquedas de autor: NO sumar título al score bajo NINGUNA CIRCUNSTANCIA
        # Solo buscamos por autor
        pass  # Ignorar completamente
    else:
        score += int(title_match * 3 * priority["title"])

    # Categoría - dar mayor peso si intent es "category"
    category_match = fuzzy_score(normalized_query, category)
    score += int(category_match * 1.5 * priority["category"])

    # Descripción - peso menor
    description_match = fuzzy_score(normalized_query, description)
    score += int(description_match * 0.5 * priority["description"])

    # ISBN - si intent es ISBN, dar máximo peso
    if priority.get("isbn", 0) > 0 and book.isbn:
        isbn_normalized = book.isbn.replace("-", "").replace(" ", "")
        query_normalized_isbn = normalized_query.replace("-", "").replace(" ", "")
        if query_normalized_isbn in isbn_normalized or isbn_normalized in query_normalized_isbn:
            score += 1000  # Máximo bonus para coincidencia ISBN exacta

    # Si el título tiene todos los términos principales de la query
    # (Solo aplicar si title_q no es None)
    query_keywords = set()
    title_words = set(title.split())

    if title_q:
        query_words = set(title_q.split())
        stopwords_basic = {"el", "la", "los", "las", "de", "del", "y", "un", "una", "autor"}
        query_keywords = {w for w in query_words if w and w not in stopwords_basic}
        common_keywords = query_keywords & title_words
        if len(common_keywords) > 0:
            coverage = len(common_keywords) / len(query_keywords) if query_keywords else 0
            score += int(coverage * 30)  # Bonus por cobertura de palabras clave
        else:
            # ⚠️ PENALIZACIÓN: Si la query tiene palabras clave específicas (no genéricas)
            # y el título NO las contiene, penalizar fuerte
            # PERO: si intent es "author", ser menos estricto con el título
            if query_keywords and intent != "author" and author_match_author < 80:
                score -= 300  # Penalización fuerte por falta de keywords
                score -= int(title_match * 2)  # Neutralizar fuzzy parcial con títulos no relacionados

    # Penalización extra si los keywords largos no aparecen ni son similares en el título
    # Evita que palabras como "alquimista" se confundan con "quimica"
    # (Solo si es búsqueda de título)
    if title_q and author_match_author < 80:
        long_keywords = [w for w in query_keywords if len(w) >= 6]
        if long_keywords:
            for kw in long_keywords:
                matched = False
                for tw in title_words:
                    if kw in tw:
                        matched = True
                        break
                    if levenshtein_distance(kw, tw) <= 2:
                        matched = True
                        break
                if not matched:
                    score -= 400


    # 📏 Priorización de ediciones y penalización de spin-offs
    # 1. Edición estándar (título simple, sin sufijos): 50 puntos
    # 2. Edición ILUSTRADO: 15 puntos
    # 3. Edición especial con "AÑO X" (MINALIMA): 10 puntos
    # 4. Ediciones con descripciones largas: 5 puntos
    # Penalización: Spin-offs y ediciones derivadas: -50 puntos

    title_text = book.title or ""
    title_upper = title_text.upper()

    edition_priority = 0

    # Detectar spin-offs y ediciones secundarias (PENALIZACIÓN)
    # Estos son libros que mencionan el título principal pero no son el libro principal
    spin_off_indicators = [
        "NAVIDAD EN", "DE HARRY POTTER", "DEL UNIVERSO DE",
        "FRAGMENTO", "COMPANION", "GUIA", "GUIDE", "COLORING",
        "ANIMALES FANTASTICOS", "MARAVILLAS DE LA NATURALEZA"
    ]

    if any(indicator in title_upper for indicator in spin_off_indicators):
        edition_priority = -50  # Penalización fuerte para spin-offs

    # Detectar edición MINALIMA (tiene "AÑO" en el título) o descripciones largas
    elif any(phrase in title_text for phrase in ["Diseño e ilustraciones", "diseño", "ilustraciones de MINALIMA"]):
        edition_priority = 5  # Cuarta prioridad
    elif "AÑO" in title_upper or "ANO" in title_upper:
        edition_priority = 10  # Tercera prioridad
    # Detectar edición ILUSTRADO (segunda prioridad)
    elif "ILUSTRADO" in title_upper:
        edition_priority = 15  # Segunda prioridad
    # Detectar otras ediciones especiales
    elif any(word in title_upper for word in ["T/D", "TAPA DURA", "EDICION"]):
        edition_priority = 8  # Entre ILUSTRADO y AÑO
    # Título simple (estándar) - MÁXIMA PRIORIDAD
    else:
        edition_priority = 50  # Primera prioridad (máxima)

    score += edition_priority

    # ✍️ Autor/Editorial
    if author_q:
        author_score = max(
            fuzzy_score(author_q, author),
            fuzzy_score(author_q, publisher),
        )
        score += int(author_score * 1.5 * priority["author"])

    # 📚 Categoría (peso ajustable según intent)
    category_score = fuzzy_score(title_q, category)
    score += int(category_score * 0.5 * priority["category"])

    # 📖 Descripción como último recurso (peso ajustable según intent)
    desc_score = fuzzy_score(title_q, description)
    score += int(desc_score * 0.3 * priority["description"])

    # 📊 Bonus por stock disponible
    if book.stock and book.stock > 0:
        score += min(book.stock * 1.5, 15)  # Máximo bonus de 15 puntos

    return int(score)


def rerank_books(books: List[Book], query: str, boost_ids: Optional[set] = None) -> List[Book]:
    scored = [(score_book(book, query), book) for book in books]

    # Si hay IDs para boostear (libros del alias), les damos +500 puntos extra
    if boost_ids:
        scored = [
            (score + 500 if book.id in boost_ids else score, book)
            for score, book in scored
        ]

    # Si la query NO tiene número, ordenar por número ascendente cuando
    # la mayoría de resultados parecen ser de un mismo autor con numeración.
    import re
    query_numbers = re.findall(r"\d+", query)

    def series_number(title: str) -> int:
        match = re.search(r"\b(\d+)\b", title or "")
        return int(match.group(1)) if match else 10**9

    if not query_numbers:
        series_author_count = 0
        for _, book in scored:
            if series_number(book.title) != 10**9 and fuzzy_score_author(query, book.author or "") >= 80:
                series_author_count += 1
        if series_author_count >= 3:
            scored.sort(key=lambda x: (series_number(x[1].title), -x[0]))
        else:
            scored.sort(key=lambda x: x[0], reverse=True)
    else:
        scored.sort(key=lambda x: x[0], reverse=True)

    return [book for _, book in scored]