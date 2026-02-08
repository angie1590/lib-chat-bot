query = 'García maquez'
author = 'GARCIA MARQUEZ, GABRIEL'
query_words = query.lower().split()
author_lower = author.lower()
print(f'Query words: {query_words}')
print(f'Author lower: {author_lower}')
for word in query_words:
    found = word in author_lower
    print(f'  {word!r} in author? {found}')
