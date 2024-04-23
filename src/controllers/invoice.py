from fastapi import APIRouter, Response
from service import InvoiceService
from util import DatabaseSession, RedisSession, FileUpload
from dtypes import GenInvoiceRequest, make_response

router = APIRouter(prefix="/api/v1/invoice", tags=["invoice"])
invoice_service = InvoiceService(
    db_session=DatabaseSession(),
    redis_session=RedisSession(),
    file_upload=FileUpload()
)

@router.post("/")
async def generate_invoice(request: GenInvoiceRequest, response: Response):
    try:
        success, data = await invoice_service.generate_invoice(request.order_id)
        if not success:    
            return make_response(response, 500, "Failed to generate invoice", None)
        return make_response(response, 201, "Invoice generated successfully", data)
    except Exception as e:
        print(e)
        return make_response(response, 500, str(e), None)

@router.get("/{order_id}")
async def get_invoice(order_id: str, response: Response):
    data = invoice_service.get_invoice(order_id)
    if not data:
        return make_response(response, 404, "Invoice not found", None)
    return make_response(response, 200, "Invoice found", data)