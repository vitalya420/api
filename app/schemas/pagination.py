from pydantic import BaseModel, field_validator


class PaginationQuery(BaseModel):
    """
    A class to represent pagination parameters for querying data.

    This class encapsulates the pagination logic, allowing users to specify
    the page number and the number of items per page. It includes validation
    to ensure that the values for page and per_page are within acceptable limits.

    Attributes:
        page (int): The page number to retrieve. Defaults to 1.
        per_page (int): The number of items to return per page. Defaults to 20.

    Methods:
        limit_per_page(value: int) -> int:
            Validates and limits the per_page value to a maximum of 20 and a minimum of 1.

        page_validate(value: int) -> int:
            Validates the page number to ensure it is at least 1.

        limit() -> int:
            Returns the number of items to return per page.

        offset() -> int:
            Calculates the offset based on the current page and items per page.
    """

    page: int = 1
    per_page: int = 20

    @field_validator("per_page")  # noqa
    @classmethod
    def limit_per_page(cls, value):
        return min(max(value, 1), 20)  # Ensure per_page is at least 1 and at most 20

    @field_validator("page")  # noqa
    @classmethod
    def page_validate(cls, value):
        return max(1, value)  # Ensure page is at least 1

    @property
    def limit(self) -> int:
        """Returns the number of items to return per page."""
        return self.per_page

    @property
    def offset(self) -> int:
        """Calculates the offset based on the current page and items per page."""
        return (self.page - 1) * self.per_page
