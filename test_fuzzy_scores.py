from rapidfuzz import fuzz

query = "garcia maquez"
author = "garcia marquez, gabriel"

score = fuzz.partial_ratio(query, author)
print(f"Query: '{query}'")
print(f"Author: '{author}'")
print(f"Partial ratio score: {score}")

# Probar diferentes métodos
print(f"\ntoken_sort_ratio: {fuzz.token_sort_ratio(query, author)}")
print(f"ratio: {fuzz.ratio(query, author)}")
print(f"token_set_ratio: {fuzz.token_set_ratio(query, author)}")
