from typing import List
from pydantic import BaseModel, Field


class Pageable(BaseModel):
    """
    Model representing a pageable response.

    Attributes:
        content (List): The list of content in the current page.
        totalPages (int): Total number of pages.
        totalElements (int): Total number of elements across all pages.
        last (bool): Indicates if this is the last page.
        size (int): Size of each page.
        number (int): Current page number.
        sort (List[str]): Sorting criteria.
        numberOfElements (int): Number of elements in the current page.
        first (bool): Indicates if this is the first page.
        empty (bool): Indicates if the current page is empty.

    Example usage:
        ```
        content = ["item1", "item2"]
        total_elements = 10
        page_number = 0
        page_size = 2
        sort_criteria = ["field1", "-field2"]

        pageable_response = create_pageable_response(content, total_elements, page_number, page_size, sort_criteria)
        ```
    """

    content: List = Field(description="The list of content")
    totalPages: int = Field(description="Total number of pages")
    totalElements: int = Field(description="Total number of elements")
    last: bool = Field(description="Indicates if this is the last page")
    size: int = Field(description="Size of the page")
    number: int = Field(description="Current page number")
    sort: List[str] = Field(description="Sorting criteria", default=[])
    numberOfElements: int = Field(description="Number of elements in the current page")
    first: bool = Field(description="Indicates if this is the first page")
    empty: bool = Field(description="Indicates if the current page is empty")


def create_pageable_response(content: list, total_elements: int, page_number: int, size: int,
                             sort: List[str]) -> Pageable:
    """
    Create a pageable response object.

    Args:
        content (list): List of content items for the current page.
        total_elements (int): Total number of elements across all pages.
        page_number (int): Current page number (starting from 0).
        size (int): Size of each page.
        sort (List[str]): Sorting criteria.

    Returns:
        Pageable: Instance of Pageable representing the paginated response.
    """
    return Pageable(
        content=content,
        totalPages=(total_elements + size - 1) // size,
        totalElements=total_elements,
        last=(page_number + 1) * size >= total_elements,
        size=size,
        number=page_number,
        sort=sort,
        numberOfElements=len(content),
        first=page_number == 0,
        empty=len(content) == 0
    )
