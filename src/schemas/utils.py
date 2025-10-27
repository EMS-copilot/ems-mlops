from typing import Annotated
from pydantic import BaseModel, Field


class Coord(BaseModel):
    x: Annotated[int, Field(ge=0, le=100)]
    y: Annotated[int, Field(ge=0, le=100)]
