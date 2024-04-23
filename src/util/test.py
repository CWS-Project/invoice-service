from string import Template
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent

def get_table_row_from_product(i: int, product: dict, currency: str) -> str:
    return f"""
        <tr>
            <td>{i}</td>
            <td>{product['name']}</td>
            <td>{currency} {product['price']}</td>
            <td>{product['qty']}</td>
            <td>{currency} {product['qty']*product['price']}</td>
        </tr>
    """

with open(BASE_PATH / "template" / "invoice.html") as html_template:
        template = Template(html_template.read())
        products = [
            {
                "name": "Product 1",
                "price": 100,
                "qty": 2
            },
            {
                "name": "Product 2",
                "price": 200,
                "qty": 1
            }
        ]

        total = sum([product['price'] * product['qty'] for product in products])
        tax = round(total * 0.18, 2)
        grand_total = round(total + tax, 2)

        data = {
              "invoice_id": "INV-123",
                "customer_name": "John Doe",
                "currency": "INR",
                "amount_paid": grand_total,
                "email": "johndoe@gmail.com",
                "phone": "1234567890",
                "line1": "123, Main Street",
                "line2": "Near Park",
                "city": "New York",
                "state": "NY",
                "country": "USA",
                "postal_code": "10001",
                "date": "2021-12-01",

                "items": "".join([get_table_row_from_product(i+1, product, "INR") for i, product in enumerate(products)]),
                "lastno": len(products) + 1,
                "tax": tax,
                "grand_total": grand_total,
                "payment_id": "N/A",
                "payment_date": "N/A",
                "payment_status": "Not Paid",
                "payment_method": "N/A",
        }
        pdf_str = template.substitute(data)
        with open("test_inv.html", "w") as f:
            f.write(pdf_str)