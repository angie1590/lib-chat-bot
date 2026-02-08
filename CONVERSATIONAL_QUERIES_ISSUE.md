# Problema: Búsquedas Conversacionales

## Query Problemática
**"quiero libros que hablen de García Márquez"**

### Comportamiento Actual
1. **Intent Detectado**: `title` (incorrecto - debería detectar como `author`)
2. **Palabras extraídas**: `{'quiero', 'libros', 'que', 'hablen', 'de', 'garcía', 'márquez'}`
3. **Resultados**: 1,775 libros encontrados
4. **Top resultados**: Libros **SOBRE** García Márquez, no **DE** García Márquez
   - "LECTURAS COMPLICES En busca de García Márquez, Cortázar y Onetti"
   - "SOLEDAD & COMPAÑIA un retrato compartido de Gabriel García Márquez"
   - "GABRIEL GARCIA MARQUEZ Y EL CINE"

### Problemas Identificados
1. **Intent Detection**: Con >3 palabras, se clasifica como "title" en lugar de "author"
2. **Palabra "hablen"**: Se interpreta como búsqueda en título/autor, encontrando cualquier libro con esas palabras
3. **Falta de contexto**: No distingue "libros DE García Márquez" vs "libros que hablan DE García Márquez"

## Comparación: Queries Simples vs Conversacionales

| Query | Intent | Resultados |
|-------|--------|-----------|
| "García Márquez" | title | ✅ 5 obras de GARCIA MARQUEZ en orden 1-5 |
| "García maquez" | title | ✅ GARCIA MARQUEZ, GABRIEL (typo handling) |
| "libros de García Márquez" | title | ❌ Devuelve 1,775 libros |
| "quiero libros que hablen de García Márquez" | title | ❌ Devuelve 1,775 libros (SOBRE él, no DE él) |

## Solución Propuesta
Mejorar `detect_query_intent()` para:
1. Detectar palabras clave como "de", "por", "autor" que indican búsqueda de autor
2. Extraer solo las palabras relevantes (apellidos/nombres) de frases conversacionales
3. Priorizar búsqueda de autor cuando se detectan patrones como:
   - "libros de [AUTOR]"
   - "obras de [AUTOR]"
   - "escritos por [AUTOR]"
   - "[AUTOR] es un autor" (donde el usuario quiere libros del autor)

## Alternativa: Normalizador de Queries
Crear una función que simplifique queries conversacionales:
- "quiero libros que hablen de García Márquez" → "García Márquez"
- "libros de García Márquez" → "García Márquez"
- "obras escritas por García Márquez" → "García Márquez"
