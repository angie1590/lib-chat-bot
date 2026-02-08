from lib_chat_bot.catalog.client import search_books


def test_search_returns_exact_book_first():
    query = "GESTION AMBIENTAL EN LA EMPRESA"

    books = search_books(query)

    assert len(books) > 0, "La búsqueda no devolvió resultados"

    first_book = books[0]

    assert query in first_book.title.upper()