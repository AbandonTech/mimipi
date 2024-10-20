from pydantic import BaseModel

class Product(BaseModel):
    upc: str | None
    name: str
    details: str
    weight: int
    barcode: str
