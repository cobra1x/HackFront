system_prompt="""
    Analyze all the provided invoice and payment receipt documents.

    For each invoice:
    1. Find the invoice date and invoice ID and payment terms or payment due date .
    2. Find the corresponding payment receipt.
    3. Find the payment date.
    4. Calculate payment delay in days.
    5. If payment was not received, discard that invoice from the calculation.

    Finally calculate the average payment delay using only invoices
    for which payment was received.

    Return ONLY the average payment delay as an integer.
    Do not return JSON, markdown, explanation, or decimal values.
    **IMPORTANT:recheck the calculations again so that no scope of error**
    """