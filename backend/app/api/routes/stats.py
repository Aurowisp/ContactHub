from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.contact import StatsResponse
from app.services.contact_service import get_stats


router = APIRouter(tags=["statistics"])


@router.get("/stats", response_model=StatsResponse)
def statistics(db: Session = Depends(get_db)):
    return get_stats(db)

