from fastapi import APIRouter,UploadFile, File
from typing import List
from app.core.llm import client
from app.templates.system_prompt import system_prompt

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

