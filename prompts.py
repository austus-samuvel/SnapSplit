RECEIPT_PROMPT = """
Read this receipt and return ONLY valid JSON.

Use this format:

{
    "restaurant_name": "string",
    "category": "string",
    "items": [
        {
            "name": "string",
            "quantity": 0,
            "rate": 0.0,
            "amount": 0.0
        }
    ],
    "subtotal": 0.0,
    "tax": 0.0,
    "total": 0.0
}

Category must be one of:
Food, Groceries, Transport, Shopping,
Entertainment, Medical, Utilities, Other.

Add all taxes together.

Return only JSON.
"""