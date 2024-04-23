from typing import AnyStr, Optional, Tuple
from pathlib import Path
from util import DatabaseSession, RedisSession, FileUpload, get_order_from_id, get_payment_from_id, get_user_from_id, get_invoice_markdown_str
from playwright.async_api import async_playwright
from bson.objectid import ObjectId


class InvoiceService:
    __db_session: DatabaseSession
    __redis_session: RedisSession
    __file_upload: FileUpload

    def __init__(self, db_session: DatabaseSession, redis_session: RedisSession, file_upload: FileUpload):
        self.__db_session = db_session
        self.__redis_session = redis_session
        self.__file_upload = file_upload

    def _get_invoice_db(self, order_id: str) -> Optional[str]:
        success, data = self.__db_session.findOne("invoices", {"order_id": order_id})
        if not success:
            return None
        if not data:
            return None
        return data["invoice_url"]

    def get_invoice(self, order_id: str) -> Optional[dict]:
        invoice = self.__redis_session.get(f"invoice:{order_id}")
        if invoice is None:
            invoice = self._get_invoice_db(order_id)
            if not invoice:
                return None
            self.__redis_session.set(f"invoice:{order_id}", invoice, 120)
        return {"invoice_url": invoice}
    
    def upload_invoice(self, invoice_id: AnyStr, file: Path) -> Optional[str]:
        success, url = self.__file_upload.upload_file(file, f"{invoice_id}.pdf")
        if not success:
            return None
        return url

    async def generate_invoice(self, order_id: str) -> Tuple[bool, str | dict]:
        order = get_order_from_id(order_id)
        if not order:
            print(f"Order not found: {order_id}")
            return False, None
        
        check = self.get_invoice(order_id)
        if check:
            print(f"Invoice already exists: {order_id}")
            return False, "Invoice already exists!"
        
        # payment = get_payment_from_id(payment_id)
        # if not payment:
        #     return False, "Payment not found!"
        
        user = get_user_from_id(order["user_id"])
        if not user:
            print(f"User not found: {order['user_id']}")
            return False, "User not found!"

        customer_name = f"{user['first_name']} {user['last_name']}"
        email = user['email']
        phone = user['phone']
        user_address = user['address']

        invoice_id = str(ObjectId())
        invoice = Path(f"./{invoice_id}.pdf")

        invoice_str = get_invoice_markdown_str(
            invoice_id,
            customer_name,
            order['items'],
            order['currency'].upper(),
            order['grand_total'],
            order['sub_total'],
            order['tax'],
            order['grand_total'],
            order["payment_id"],
            order["status"],
            email,
            phone,
            **user_address
        )

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            page = await browser.new_page()
            await page.set_content(invoice_str)
            await page.pdf(path=invoice, format='A4')
            await browser.close()

        
        print(f"Generated invoice: {invoice_id}")
        url = self.upload_invoice(invoice_id, invoice)
        if not url:
            print(f"Unable to upload invoice: {invoice_id}")
            return False, "Unable to Upload"
        invoice.unlink(missing_ok=True)

        success, data = self.__db_session.insert("invoices", {
            "_id": ObjectId(invoice_id),
            "order_id": order_id,
            "payment_id": order['payment_id'],
            "invoice_url": url,
            # "amount": payment['amount_paid'],
            "amount": order['grand_total'],
            "currency": order['currency']
        })

        if not success:
            return False, "Unable to save invoice in DB!"
        
        return True, {"invoice_id": data, "url": url}

    def create_and_upload_invoice(self, data: dict) -> Optional[AnyStr]:
        invoice = self.generate_invoice(data)
        invoice_url = self.upload_invoice(data["invoice_id"], invoice)
        return invoice_url if invoice_url else None
