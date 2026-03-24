
from pydantic import BaseModel

class PriceCalculated(BaseModel):
    product_id: str
    price: float
