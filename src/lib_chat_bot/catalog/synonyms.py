"""
Diccionario de sinónimos y variaciones comunes en términos editoriales y de libros.
"""

SYNONYMS = {
    # Términos de gestión y administración
    "gestion": ["gestión", "manejo", "administración", "management"],
    "ambiental": ["ambiente", "medio ambiente", "ecologico", "ecológico", "sostenible", "sustentable"],
    "empresa": ["empresarial", "corporativo", "organizacional", "negocio"],
    "calidad": ["quality", "excelencia", "estándar", "norma"],
    "competitividad": ["competencia", "ventaja competitiva", "eficiencia"],

    # Autores y editoriales comunes
    "paulo": ["paulo coelho", "paulo cohelo", "paul"],
    "coelho": ["cohelo", "paulo coelho"],
    "alquimista": ["alquimia", "alqimista"],
    # Variaciones comunes
    "desarrollo": ["desarrollar", "evolución", "crecimiento"],
    "implementacion": ["implementación", "ejecución", "puesta en marcha"],
    "fundamentos": ["fundación", "base", "principios"],
    "lineamientos": ["lineamiento", "directriz", "guía"],
    "comunicacion": ["comunicaciones", "medios"],
    "sustentabilidad": ["sustentable", "sostenible", "sostenibilidad"],
}

# Alias de títulos específicos para mejorar búsquedas
# Mapea queries comunes a búsquedas optimizadas
# IMPORTANTE: Todas las claves deben estar en minúsculas
TITLE_ALIASES = {
    # Harry Potter - usar "piedra filosofal" da mejores resultados que "harry potter"
    "harry potter 1": ["piedra filosofal 1", "harry potter 1"],
    "harry potte 1": ["piedra filosofal 1", "harry potte 1"],
    # Para typos severos como "jarry poter", usar SOLO el typo en alias para que aparezcan JARRIPOTER primero
    # El fallback con typo correction buscará "harry potter 1" después
    # ⚠️ IMPORTANTE: SOLO cuando hay número específico "1"
    "jarry poter 1": ["jarripoter 1", "jarripoter"],

    # Para búsquedas sin número, ir directo a "harry potter" (sin JARRIPOTER)
    "harry potter y la piedra filosofal": ["piedra filosofal 1", "piedra filosofal", "harry potter piedra filosofal"],
    "harry potter y la piedra filosofal 1": ["piedra filosofal 1", "harry potter piedra filosofal 1"],

    # Búsquedas de ediciones específicas
    "harry potter ilustrado": ["harry potter ilustrado"],
    "ahrry poter ilustrado": ["harry potter ilustrado"],  # Typo + edición
    "harry potte ilustrado": ["harry potter ilustrado"],   # Typo + edición

    # El Alquimista (evitar ruido como "química")
    # Nota: El Alquimista exacto no está en SODILIBRO
    # Preferir buscar libros de Paulo Coelho disponibles
    "el alquimista": ["paulo coelho"],
    "el alqimsta": ["paulo coelho"],
}

# Expansiones inversa: para cada valor, agregar entrada que mapee al equivalente normalizado
NORMALIZED_SYNONYMS = {}

for main_term, variations in SYNONYMS.items():
    NORMALIZED_SYNONYMS[main_term] = main_term
    for var in variations:
        NORMALIZED_SYNONYMS[var] = main_term


def expand_query_with_synonyms(query: str) -> list[str]:
    """
    Expande la query con sinónimos para mejorar búsquedas.

    Ejemplo:
        expand_query_with_synonyms("ambiental") ->
        ["ambiental", "ambiente", "medio ambiente", "ecologico", ...]
    """
    from .search_engine import normalize

    normalized = normalize(query)
    variations = set([query])  # Mantener original

    # Buscar sinónimos exactos
    if normalized in SYNONYMS:
        variations.update(SYNONYMS[normalized])

    # También buscar en las variaciones inversas
    for var in normalize(query).split():
        if var in NORMALIZED_SYNONYMS:
            main = NORMALIZED_SYNONYMS[var]
            if main in SYNONYMS:
                variations.update(SYNONYMS[main])

    return list(variations)


def normalize_with_synonyms(text: str) -> str:
    """
    Normaliza un texto reemplazando términos con sus sinónimos principales.
    Útil para mejorar coincidencias en el scoring.
    """
    from .search_engine import normalize

    normalized = normalize(text)
    words = normalized.split()

    expanded = []
    for word in words:
        if word in NORMALIZED_SYNONYMS:
            main_term = NORMALIZED_SYNONYMS[word]
            expanded.append(main_term)
        else:
            expanded.append(word)

    return " ".join(expanded)
