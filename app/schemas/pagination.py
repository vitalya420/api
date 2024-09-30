from typing import Optional

from pydantic import BaseModel, conint


class PaginationQuery(BaseModel):
    page: Optional[int] = 1
    per_page: Optional[conint(le=20)] = 20
