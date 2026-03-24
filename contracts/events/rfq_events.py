
from pydantic import BaseModel
from datetime import datetime

class RFQReceived(BaseModel):
    schema_version: str = "1.0"
    rfq_id: str
    attachments: list[str]
    created_at: datetime
