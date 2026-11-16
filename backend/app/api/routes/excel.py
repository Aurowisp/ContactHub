from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.contact import ImportResult
from app.services.excel_service import MAX_UPLOAD_SIZE, create_template, export_contacts, import_contacts


router = APIRouter(prefix="/contacts", tags=["excel"])
XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def download(content: bytes, filename: str) -> Response:
    return Response(
        content=content,
        media_type=XLSX_MEDIA,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export")
def export_file(db: Session = Depends(get_db)):
    return download(export_contacts(db), f"contacthub_export_{date.today().isoformat()}.xlsx")


@router.get("/import-template")
def import_template():
    return download(create_template(), "contacts_template.xlsx")


@router.post("/import", response_model=ImportResult)
async def import_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")
    content = await file.read(MAX_UPLOAD_SIZE + 1)
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds the 10 MB upload limit")
    try:
        return import_contacts(db, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

