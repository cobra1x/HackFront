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
        model="gemini-3.5-flash-lite",
        contents=[system_prompt]+contents
    )

    return {"output":res.text}

@router.post("/liquidity")
def liquidity(data: LiquidityInput):

    if data.past_delay_days is None:
        risk_score = 65 - (data.buyer_tier * 5) - (data.tenor_days * 0.1)
        history_status = "NEW_CUSTOMER"
    else:
        risk_score = 100 - (data.past_delay_days * 2) - (data.tenor_days * 0.2) - (data.buyer_tier * 5)
        history_status = "HISTORICAL"

    risk_score = max(0, min(100, risk_score))

    if risk_score >= 80:
        advance_rate = 0.90
        risk_tier = "LOW"
    elif risk_score >= 65:
        advance_rate = 0.75
        risk_tier = "MODERATE"
    elif risk_score >= 50:
        advance_rate = 0.60
        risk_tier = "ELEVATED"
    elif history_status == "NEW_CUSTOMER":
        advance_rate = 0.40
        risk_tier = "HIGH"
    else:
        advance_rate = 0
        risk_tier = "REJECT"

    if advance_rate == 0:
        return {
            "risk_score": round(risk_score),
            "risk_tier": risk_tier,
            "status": "REJECT",
            "advance_rate": 0,
            "net_advance_amount": 0,
            "discount_fee": 0,
            "reserve_amount": data.invoice_amount
        }

    principal = data.invoice_amount * advance_rate
    fee = principal * (0.025 + 0.005) * (data.tenor_days / 360)
    reserve = data.invoice_amount - principal
    net_advance = principal - fee

    return {
        "risk_score": round(risk_score),
        "risk_tier": risk_tier,
        "status": "APPROVE",
        "advance_rate": advance_rate,
        "net_advance_amount": round(net_advance, 2),
        "discount_fee": round(fee, 2),
        "reserve_amount": round(reserve, 2)
    }