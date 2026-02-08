from pydantic import BaseModel
from typing import Optional


class Book(BaseModel):
    id: int
    title: str

    author: Optional[str] = None        # Autor real
    publisher: Optional[str] = None     # Editorial

    category: Optional[str] = None
    subcategory: Optional[str] = None

    price: Optional[float] = None
    stock: Optional[int] = None
    isbn: Optional[str] = None
    description: Optional[str] = None