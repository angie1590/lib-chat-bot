#!/usr/bin/env python
import sys
sys.path.insert(0, 'src')

from lib_chat_bot.catalog.search_engine import fuzzy_score_author, normalize

query = "García maquez"
author = "GABRIEL GARCIA MARQUEZ"

normalized_q = normalize(query)
score = fuzzy_score_author(normalized_q, author)

print(f"Query: '{query}' → '{normalized_q}'")
print(f"Author: '{author}'")
print(f"Fuzzy Score (Author-specialized): {score}")

# Probar otros casos
test_cases = [
    ("García maquez", "GABRIEL GARCIA MARQUEZ"),
    ("García Márquez", "GABRIEL GARCIA MARQUEZ"),
    ("marquez", "GABRIEL GARCIA MARQUEZ"),
    ("garcia", "GABRIEL GARCIA MARQUEZ"),
    ("José ZAPATA", "ZAPATA, JAIME"),
    ("zapata", "ZAPATA, JAIME"),
]

print("\n=== TEST CASES ===")
for q, a in test_cases:
    s = fuzzy_score_author(normalize(q), a)
    print(f"{q:25} vs {a:35} = {s:3}")
