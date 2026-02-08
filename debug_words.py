import sys
sys.path.insert(0, 'src')

from lib_chat_bot.catalog.search_engine import normalize
from rapidfuzz.fuzz import ratio

query = "garcia maquez"
author = "GARCIA MARQUEZ, GABRIEL"

query_norm = normalize(query)
author_norm = normalize(author)

query_words = set(w for w in query_norm.split() if len(w) > 2)
author_words = set(w for w in author_norm.split() if len(w) > 2)

print(f"Query: '{query}' → '{query_norm}'")
print(f"Author: '{author}' → '{author_norm}'")
print(f"\nQuery words: {query_words}")
print(f"Author words: {author_words}")
print(f"\nExact matches: {query_words & author_words}")
print(f"Exact match count: {len(query_words & author_words)}")

# Verificar fuzzy matching
print("\nFuzzy scores por palabra:")
for qw in query_words:
    print(f"\n'{qw}' vs:")
    for aw in author_words:
        score = ratio(qw, aw)
        print(f"  '{aw}': {score:.1f}")
