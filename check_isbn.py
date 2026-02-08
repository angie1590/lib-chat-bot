#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd

df = pd.read_excel('SDLLista14nov2025.xlsx')

# Buscar el ISBN
isbn = '9781567182811'
results = df[df['ISBN'].astype(str).str.contains(isbn, na=False)]

if len(results) > 0:
    print(f"✅ ISBN ENCONTRADO: {len(results)} libro(s)")
    for idx, row in results.iterrows():
        print(f"\n  ISBN: {row['ISBN']}")
        print(f"  Título: {row['TITULO']}")
        print(f"  Autor: {row['AUTOR']}")
        print(f"  Editorial: {row.get('EDITORIAL', 'N/A')}")
else:
    print(f"❌ ISBN NO ENCONTRADO en base de datos")
    print(f"\nChecking ISBN column type and sample values:")
    print(f"Column type: {df['ISBN'].dtype}")
    print(f"\nFirst 10 ISBNs:")
    for i, isbn_val in enumerate(df['ISBN'].head(10)):
        print(f"  {i}: {isbn_val} (type: {type(isbn_val).__name__})")
