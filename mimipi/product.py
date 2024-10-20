from pydantic import BaseModel

class Product(BaseModel):
    upc: str | None
    name: str | None
    details: str | None
    weight: int | None
