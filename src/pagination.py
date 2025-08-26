from typing import Generic, Sequence, TypeVar

from fastapi import Query
from pydantic.generics import GenericModel

# Define a generic TypeVar for Pydantic models
T = TypeVar("T")


class PaginationParams:
    """
    A dependency class to handle pagination query parameters.
    """

    def __init__(
            self,
            page: int = Query(1, ge=1, description="Page number"),
            size: int = Query(10, ge=1, le=100, description="Page size"),
    ):
        self.page = page
        self.size = size
        self.offset = (page - 1) * size


class Page(GenericModel, Generic[T]):
    """A generic Pydantic model for paginated API responses."""
    items: Sequence[T]
    total: int
    page: int
    size: int
