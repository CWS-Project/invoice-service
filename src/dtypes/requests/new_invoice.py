from pydantic import BaseModel

class GenInvoiceRequest(BaseModel):
    order_id: str