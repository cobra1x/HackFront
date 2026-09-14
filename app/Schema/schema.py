from pydantic import BaseModel

class LiquidityInput(BaseModel):
    invoice_amount: float
    buyer_tier: int
    tenor_days: int
    past_delay_days: int | None = None
    industry: str
    