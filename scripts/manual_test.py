import sys
from pathlib import Path

# Agregar src/ al path para importar lib_chat_bot
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from lib_chat_bot.catalog.client import search_books


def print_results(query: str, limit: int = 5):
    print("\n" + "=" * 80)
    print(f"Consulta: {query}")
    print("=" * 80)

    books = search_books(query)

    for i, book in enumerate(books[:limit], start=1):
        print(
            f"{i}. {book.title} | "
            f"Autor: {book.author} | "
            f"Stock: {book.stock}"
        )


if __name__ == "__main__":
    test_queries = [
        "GESTION AMBIENTAL EN LA EMPRESA",
        "gestion anbiental en la enpresa",
        "el alquimista",
        "el alqimsta",
        "el alquimista del autor pablo cuello",
        "libro el alqimsta paulo cohelo",
        "busco un libro de gestion ambiental",
        "harry potte 2",
        "harry potter 1",
        "jarry poter 2",
        "jarry poter 1",
        "Harry Potter legado maldito",
        "HARRY POTTER Y LA PIEDRA FILOSOFAL",
        "ahrry poter ilustrado",
    ]

    for q in test_queries:
        print_results(q)