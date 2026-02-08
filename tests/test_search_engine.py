from lib_chat_bot.catalog.search_engine import score_book, rerank_books
from lib_chat_bot.catalog.models import Book


def test_exact_title_is_ranked_first():
    query = "GESTION AMBIENTAL EN LA EMPRESA"

    books = [
        Book(id=1, title="GESTION DE LA COMPETITIVIDAD EMPRESARIAL", price=10, stock=1),
        Book(id=2, title="GESTION AMBIENTAL EN LA EMPRESA", price=20, stock=1),
        Book(id=3, title="FUNDAMENTOS EN MEDIO AMBIENTE Y GESTION DE RESIDUOS", price=15, stock=1),
    ]

    ranked = rerank_books(books, query)

    assert ranked[0].title == query

def test_fuzzy_title_and_author_with_typos():
    from lib_chat_bot.catalog.search_engine import rerank_books
    from lib_chat_bot.catalog.models import Book

    books = [
        Book(id=1, title="EL ALQUIMISTA", author="Paulo Coelho"),
        Book(id=2, title="EL PODER DEL AHORA", author="Eckhart Tolle"),
    ]

    ranked = rerank_books(
        books,
        "el alqimsta del autor pablo cuello"
    )

    assert ranked[0].title == "EL ALQUIMISTA"