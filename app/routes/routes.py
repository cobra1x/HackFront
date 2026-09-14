from fastapi import APIRouter,UploadFile, File
from typing import List
from app.core.llm import client
from app.templates.system_prompt import system_prompt
from app.Schema.schema import LiquidityInput

router=APIRouter()
contents = []



@router.get("/")
def home():
    return {"message":"hello from server"}

@router.post("/document/upload")
def upload(files:list[UploadFile] = File(...)):
    for file in files:
        with open(f"docs/{file.filename}", "wb") as f:
            f.write(file.file.read())

        gemini_files=client.files.upload(file=f"docs/{file.filename}")
        contents.append(gemini_files)

    return {"message": "Files uploaded successfully"}
    # name=None

@router.get("/delay_average")
def delay_average():
    res=client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[system_prompt]+contents
    )

    return {"output":res.text}

@router.post("/liquidity")
def liquidity(data: LiquidityInput):

    if data.past_delay_days is None:
        risk_score = 45
        advance_rate = 0.45
    else:
        risk_score = 100 - (data.past_delay_days * 2) - (data.tenor_days * 0.2) + (data.buyer_tier * 5)
        risk_score = max(0, min(100, risk_score))

        if risk_score >= 80:
            advance_rate = 0.90
        elif risk_score >= 65:
            advance_rate = 0.75
        elif risk_score >= 50:
            advance_rate = 0.60
        else:
            advance_rate = 0.40

    principal = data.invoice_amount * advance_rate

    fee = principal * (0.025 + 0.005) * (data.tenor_days / 360)
    reserve = data.invoice_amount - principal
    net_advance = principal - fee

    return {
        "risk_score": round(risk_score),
        "advance_rate": advance_rate,
        "net_advance_amount": round(net_advance, 2),
        "discount_fee": round(fee, 2),
        "reserve_amount": round(reserve, 2)
    }