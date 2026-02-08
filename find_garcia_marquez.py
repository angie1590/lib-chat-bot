#!/usr/bin/env python
import pandas as pd

df = pd.read_excel("SDLLista14nov2025.xlsx")

# Buscar exactamente "GARCIA MARQUEZ, GABRIEL"
print("=== BÚSQUEDA EXACTA: 'GARCIA MARQUEZ, GABRIEL' ===")
gm_books = df[df['AUTOR'].str.contains('GARCIA MARQUEZ, GABRIEL', case=False, na=False, regex=False)]

print(f"Encontrados: {len(gm_books)} libros\n")

if len(gm_books) > 0:
    for idx, row in gm_books.head(10).iterrows():
        print(f"TÍTULO: {row['TITULO']}")
        print(f"AUTOR: {row['AUTOR']}")
        print(f"Stock: {row['Existencia']}")
        print("-" * 80)
else:
    # Buscar variantes
    print("No encontrado con ese formato exacto. Buscando variantes...")
    variants = df[df['AUTOR'].str.contains('MARQUEZ.*GABRIEL|GABRIEL.*MARQUEZ', case=False, na=False)]
    print(f"\nVariantes encontradas: {len(variants)}")
    for idx, row in variants.head(10).iterrows():
        print(f"  AUTOR: {row['AUTOR']}")
        print(f"  TÍTULO: {row['TITULO'][:60]}")
        print()
