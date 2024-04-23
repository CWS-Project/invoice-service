import requests
import os
from typing import Optional, AnyStr
from datetime import datetime
from string import Template
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent




def get_order_from_id(order_id: AnyStr) -> Optional[dict]:
    response = requests.get(f"{os.getenv('ORDER_SVC_URL')}/api/v1/orders/?q={order_id}&q_type=id")
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None


def get_payment_from_id(payment_id: AnyStr) -> Optional[dict]:
    response = requests.get(f"{os.getenv('PAYMENT_SVC_URL')}/api/v1/payments/status/{payment_id}")
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None

def get_table_row_from_product(i: int, product: dict, currency: str) -> str:
    return f"""
        <tr>
            <td>{i}</td>
            <td>{product['name']}</td>
            <td>{currency} {product['price']}</td>
            <td>{product['quantity']}</td>
            <td>{currency} {product['quantity']*product['price']}</td>
        </tr>
    """

def get_user_from_id(user_id: AnyStr) -> Optional[dict]:
    response = requests.get(f"{os.getenv('AUTH_SVC_URL')}/api/v1/customer/profile/{user_id}")
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None

def get_invoice_markdown_str(
        invoice_id: AnyStr,
        customer_name: AnyStr,
        products: list,
        currency: AnyStr,
        grand_total: float,
        sub_total: float,
        tax: float,
        amount_paid: float,
        payment_id: AnyStr,
        payment_status: AnyStr,
        email: AnyStr,
        phone: AnyStr,
        line1: AnyStr,
        line2: AnyStr,
        city: AnyStr,
        state: AnyStr,
        country: AnyStr,
        district: AnyStr,
        postal_code: AnyStr,
) -> str:
    pdf_str = ""

    data = {
        "invoice_id": invoice_id.split("-")[-1],
        "customer_name": customer_name,
        "currency": currency.upper(),
        "total": sub_total,
        "tax": tax,
        "grand_total": grand_total,
        "amount_paid": amount_paid,
        "sub_total": sub_total,
        "email": email,
        "phone": phone,
        "line1": line1,
        "line2": f", {line2}" if line2 else "",
        "city": city,
        "district": district if district else "",
        "state": state,
        "country": country,
        "postal_code": postal_code,
        "items": "".join([get_table_row_from_product(i+1, product, currency) for i, product in enumerate(products)]),
        "date": datetime.now().strftime("%d-%m-%Y"),
        "lastno": len(products) + 1,
        "payment_id": payment_id,
        "payment_status": payment_status
    }

    with open(BASE_PATH / "template" / "invoice.html") as html_template:
        template = Template(html_template.read())
        pdf_str = template.substitute(data)

    return pdf_str
