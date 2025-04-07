from openai import OpenAI

from pydantic import BaseModel, Field
from datetime import date
from enum import Enum
from typing import List

# Pydantic Schemas
class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: int = Field(description="Number of units", ge=1)
    unit_price: float = Field(description="Price per unit", ge=0)

class Address(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")

class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the vendor")
    vendor_address: Address = Field(description="Vendor's address")
    invoice_number: str = Field(description="Unique invoice identifier")
    invoice_date: date = Field(description="Date the invoice was issued")
    line_items: List[LineItem] = Field(description="List of purchased items/services")
    total_amount: float = Field(description="Total amount due", ge=0)
    currency: Currency = Field(description="Currency of the invoice")

# Making the request
client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
)

completion = client.beta.chat.completions.parse(
    model="grok-2-latest",
    messages=[
        {"role": "system", "content": "Given a raw invoice, carefully analyze the text and extract the invoice data into JSON format."},
        {"role": "user", "content": """
            Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
            Invoice Number: INV-2025-001
            Date: 2025-02-10
            Items:
            - Widget A, 5 units, $10.00 each
            - Widget B, 2 units, $15.00 each
            Total: $80.00 USD
        """}
    ],
    response_format=Invoice,
)

invoice = completion.choices[0].message.parsed
print(invoice)