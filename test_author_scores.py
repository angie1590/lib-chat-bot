import sys
sys.path.insert(0, 'src')

from lib_chat_bot.catalog.search_engine import fuzzy_score_author

query = "garcia maquez"
authors = [
    "GARCIA MARQUEZ, GABRIEL",
    "GARCIA, NELSON M.",
    "FREIRE GARCIA, SUSANA"
]

print(f"Query: '{query}'\n")
for author in authors:
    score = fuzzy_score_author(query, author)
    print(f"{author:35} → Score: {score}")
