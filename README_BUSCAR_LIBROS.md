# 🔍 Buscador Interactivo de Libros

Script interactivo en línea de comandos para buscar libros en el catálogo.

## 🚀 Uso

```bash
poetry run python buscar_libros.py
```

## 📖 Características

✅ **Búsqueda por autor** - Busca libros del autor especificado
- Ejemplo: `García Márquez`, `rowlin`, `FUCOL, MICHEL`
- Soporta typos pequeños y medianos

✅ **Búsqueda por título** - Busca libros por título
- Ejemplo: `Harry Potter 1`, `jarry poter 1`, `ensayos sobre la religión`
- Soporta typos mediante fuzzy matching (70% threshold)

✅ **Búsqueda por ISBN** - Búsqueda exacta
- Ejemplo: `9781567182811`, `9786287641969`

✅ **Búsqueda conversacional** - Entiende preguntas naturales
- Ejemplo: `libros de García Márquez` → Busca obras de García Márquez
- Ejemplo: `quiero libros que hablen de García Márquez` → Busca libros SOBRE García Márquez

✅ **Múltiples búsquedas** - Realiza varias búsquedas en una sesión
- Pregunta si desea continuar después de cada búsqueda

## 🎯 Ejemplos de Búsqueda

### Búsqueda Simple de Autor
```
> García Márquez
Encontrados 35 libro(s) - Mostrando 10:
1. TEXTOS COSTEÑOS OBRA PERIODISTICA 1 1948-1952 | GARCIA MARQUEZ, GABRIEL | 942
2. ENTRE CACHACOS OBRA PERIODISTICA 2 1954-1955  | GARCIA MARQUEZ, GABRIEL | 942
...
```

### Búsqueda con Typo en Título
```
> jarry poter 1
Encontrados 67 libro(s) - Mostrando 10:
1. HARRY POTTER Y LA PIEDRA FILOSOFAL 1 ILUSTRADO | ROWLING, J.K. | 623
2. HARRY POTTER Y LA CAMARA SECRETA 2            | ROWLING, J.K. | 277
...
```

### Búsqueda por ISBN
```
> 9781567182811
Encontrados 1 libro(s) - Mostrando 1:
1. SECRETOS PERDIDOS DE LA ORACION, LOS | FINLEY, GUY | 351
```

### Búsqueda Conversacional
```
> libros de García Márquez
(Búsqueda: García Márquez)
Encontrados 35 libro(s) - Mostrando 10:
1. TEXTOS COSTEÑOS OBRA PERIODISTICA 1 1948-1952 | GARCIA MARQUEZ, GABRIEL | 942
...
```

## 🔧 Algoritmo de Búsqueda

El script utiliza un sistema inteligente que:

1. **Detecta intent** - Identifica si busca autor, título, ISBN o búsqueda general
2. **Normaliza queries** - Extrae autor de queries conversacionales
3. **Busca con exactitud** - Primero busca palabras exactas en título/autor
4. **Fallback fuzzy** - Si no encuentra exactas, busca con fuzzy matching:
   - **Autores**: 75% threshold
   - **Títulos**: 70% threshold
   - **ISBN**: 100% (exacto)

5. **Ordena resultados** - Por relevancia y detecta series de libros
6. **Limita resultados** - Muestra top 10 por defecto

## 📊 Tolerancia de Typos

| Tipo | Ejemplo | Tolerance |
|------|---------|-----------|
| Autor con typo pequeño | `ayende` → `allende` | 76.9% |
| Autor con typo medio | `fucol` → `foucault` | 61.5% (fallback 60%) |
| Título con typo | `jarry poter` → `harry potter` | 70% |
| Nombre invertido | `isabella Ayende` → `ALLENDE, ISABEL` | 75% |

## ⌨️ Comandos

```
García Márquez     - Realizar búsqueda
salir              - Terminar el programa
s                  - Sí (otra búsqueda)
n                  - No (salir)
```

## 📁 Archivos Relacionados

- `src/lib_chat_bot/catalog/search_engine.py` - Motor de búsqueda
- `src/lib_chat_bot/catalog/intent_detector.py` - Detección de intención
- `test_queries.py` - Suite de pruebas
