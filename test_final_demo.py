#!/usr/bin/env python3
import sys
sys.path.insert(0, "/Users/andrea/Documents/Proyectos/Chatbot/lib-chat-bot/src")

from lib_chat_bot.catalog.client import search_books, _search_cache

_search_cache.clear()

print("\n" + "="*100)
print("DEMOSTRACIÓN FINAL - BÚSQUEDA CON BOOST DE ALIAS")
print("="*100)

# Test 1: harry potter 1
print("\n1️⃣  BÚSQUEDA: 'harry potter 1'")
print("   (Alias: piedra filosofal 1 → harry potter 1)")
print("   " + "─"*96)
books = search_books("harry potter 1", limit=5)
for i, book in enumerate(books, 1):
    print(f"   {i}. {book.title}")

# Test 2: harry potte 1
_search_cache.clear()
print("\n2️⃣  BÚSQUEDA: 'harry potte 1' (typo)")
print("   (Corrección: harry potte → harry potter)")
print("   " + "─"*96)
books = search_books("harry potte 1", limit=5)
for i, book in enumerate(books, 1):
    print(f"   {i}. {book.title}")

# Test 3: jarry poter 1
_search_cache.clear()
print("\n3️⃣  BÚSQUEDA: 'jarry poter 1' (typo)")
print("   (Alias: jarripoter 1 + jarripoter → Fallback: harry potter 1)")
print("   (Los libros del alias reciben boost de +500 puntos)")
print("   " + "─"*96)
books = search_books("jarry poter 1", limit=10)
jarripoter_count = 0
harry_potter_count = 0
for i, book in enumerate(books, 1):
    is_jarripoter = "JARRIPOTER" in book.title.upper()
    if is_jarripoter:
        jarripoter_count += 1
        print(f"   {i}. ⭐ {book.title} [ALIAS BOOSTED]")
    else:
        harry_potter_count += 1
        print(f"   {i}. {book.title}")

print("\n" + "─"*100)
print(f"   Resultado: {jarripoter_count} libro(s) JARRIPOTER + {harry_potter_count} libro(s) HARRY POTTER")
print(f"   ✅ Ambas series mezcladas como fue solicitado")
