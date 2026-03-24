
from pydantic import BaseModel

class Product(BaseModel):
    id: str
    name: str
    manufacturer: str
    category: str | None = None
