
from pydantic import BaseModel

class RFQ(BaseModel):
    id: str
    customer: str
    products: list[str]
