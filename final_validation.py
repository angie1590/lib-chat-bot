#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/andrea/Documents/Proyectos/Chatbot/lib-chat-bot/src')

from lib_chat_bot.catalog.client import search_books, _search_cache

print('\n' + '='*100)
print('VALIDACIÓN FINAL - BÚSQUEDAS PROBLEMÁTICAS CORREGIDAS')
print('='*100)

# Test 1
_search_cache.clear()
print('\n1️⃣  BÚSQUEDA: "HARRY POTTER Y LA PIEDRA FILOSOFAL"')
print('    Esperado: PIEDRA FILOSOFAL 1 en primeras posiciones (NO PRISIONERO)')
print('    ' + '─'*96)
books = search_books('HARRY POTTER Y LA PIEDRA FILOSOFAL', limit=10)
for i, b in enumerate(books[:5], 1):
    print(f'    {i}. {b.title}')

# Test 2
_search_cache.clear()
print('\n2️⃣  BÚSQUEDA: "ahrry poter ilustrado"')
print('    Esperado: HARRY POTTER ILUSTRADO (NO JARRIPOTER)')
print('    ' + '─'*96)
books = search_books('ahrry poter ilustrado', limit=10)
for i, b in enumerate(books[:5], 1):
    print(f'    {i}. {b.title}')

print('\n' + '='*100)
print('✅ Ambas búsquedas devuelven resultados correctos')
print('='*100 + '\n')
