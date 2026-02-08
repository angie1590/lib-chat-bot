from rapidfuzz.fuzz import ratio

word1 = "maquez"
word2 = "marquez"

score = ratio(word1, word2)
print(f"'{word1}' vs '{word2}': {score}")
