from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.contact import (
    ContactCreate, ContactList, ContactRead, ContactUpdate, FavoriteUpdate,
)
from app.services import contact_service
from app.services.contact_service import ContactNotFoundError


router = APIRouter(prefix="/contacts", tags=["contacts"])


def not_found_error(exc: ContactNotFoundError) -> HTTPException:
    return HTTPException(status_code=404, detail=str(exc))


@router.get("", response_model=ContactList)
def list_contacts(
    keyword: str | None = None,
    favorite: bool | None = None,
    category: str | None = None,
    has_phone: bool | None = None,
    has_email: bool | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = contact_service.list_contacts(
        db,
        keyword=keyword,
        favorite=favorite,
        category=category,
        has_phone=has_phone,
        has_email=has_email,
        skip=skip,
        limit=limit,
    )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{contact_id}", response_model=ContactRead)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    try:
        return contact_service.get_contact(db, contact_id)
    except ContactNotFoundError as exc:
        raise not_found_error(exc) from exc


@router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact(data: ContactCreate, db: Session = Depends(get_db)):
    return contact_service.create_contact(db, data)


@router.put("/{contact_id}", response_model=ContactRead)
def update_contact(contact_id: int, data: ContactUpdate, db: Session = Depends(get_db)):
    try:
        return contact_service.update_contact(db, contact_id, data)
    except ContactNotFoundError as exc:
        raise not_found_error(exc) from exc


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    try:
        contact_service.delete_contact(db, contact_id)
    except ContactNotFoundError as exc:
        raise not_found_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{contact_id}/favorite", response_model=ContactRead)
def set_favorite(contact_id: int, data: FavoriteUpdate, db: Session = Depends(get_db)):
    try:
        return contact_service.set_favorite(db, contact_id, data.is_favorite)
    except ContactNotFoundError as exc:
        raise not_found_error(exc) from exc

