#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

query = "isabella Ayende"
words = query.split()

first_word = words[0]
second_word = words[1]

print(f"Query: '{query}'")
print(f"Words: {words}")
print(f"First word: '{first_word}' (len={len(first_word)})")
print(f"Second word: '{second_word}' (len={len(second_word)})")
print()

# Heurística 1
has_capital_or_accent_first = (len(first_word) > 0 and first_word[0].isupper()) or any(c in first_word for c in "áéíóúñü")
is_typical_name_length_first = 3 <= len(first_word) <= 9
print(f"has_capital_or_accent_first: {has_capital_or_accent_first}")
print(f"is_typical_name_length_first: {is_typical_name_length_first}")
print()

# Heurística 2
second_starts_capital = len(second_word) > 0 and second_word[0].isupper()
has_name_chars_second = any(c in second_word for c in "áéíóúñüü")
is_short = len(second_word) <= 6
print(f"second_starts_capital: {second_starts_capital}")
print(f"has_name_chars_second: {has_name_chars_second}")
print(f"is_short: {is_short}")
print()

# Heurística 3
avg_length = (len(first_word) + len(second_word)) / 2
print(f"avg_length: {avg_length} (<= 8: {avg_length <= 8})")
print()

# all_formal check
all_formal = True
for w in [first_word, second_word]:
    has_internal_capital = any(c.isupper() for c in w[1:]) if len(w) > 1 else False
    has_accent = any(c in w for c in "áéíóúñüü")
    is_short_name = len(w) < 6
    
    print(f"Word '{w}':")
    print(f"  has_internal_capital: {has_internal_capital}")
    print(f"  has_accent: {has_accent}")
    print(f"  is_short_name: {is_short_name}")
    
    if has_accent or has_internal_capital or is_short_name:
        all_formal = False

print(f"\nall_formal: {all_formal}")
print()

# Final condition
condition = (has_capital_or_accent_first or is_typical_name_length_first) and (second_starts_capital or has_name_chars_second or is_short) and avg_length <= 8
print(f"Final condition (should return 'author'): {condition}")
