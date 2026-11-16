from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.contact import Contact, ContactMethod
from app.schemas.contact import ContactCreate, ContactUpdate


class ContactNotFoundError(Exception):
    pass


def _base_query() -> Select:
    return select(Contact).options(selectinload(Contact.contact_methods))


def get_contact(db: Session, contact_id: int) -> Contact:
    contact = db.scalar(_base_query().where(Contact.id == contact_id))
    if contact is None:
        raise ContactNotFoundError(f"Contact {contact_id} not found")
    return contact


def list_contacts(
    db: Session,
    keyword: str | None = None,
    favorite: bool | None = None,
    category: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Contact], int]:
    filters = []
    if favorite is not None:
        filters.append(Contact.is_favorite.is_(favorite))
    if category:
        filters.append(func.lower(Contact.category) == category.strip().lower())
    if keyword and keyword.strip():
        pattern = f"%{keyword.strip().lower()}%"
        filters.append(or_(
            func.lower(Contact.name).like(pattern),
            func.lower(Contact.company).like(pattern),
            func.lower(Contact.job_title).like(pattern),
            Contact.contact_methods.any(func.lower(ContactMethod.value).like(pattern)),
        ))
    count = db.scalar(select(func.count(Contact.id)).where(*filters)) or 0
    query = (
        _base_query()
        .where(*filters)
        .order_by(Contact.name.asc(), Contact.id.asc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(query).all()), count


def create_contact(db: Session, data: ContactCreate) -> Contact:
    payload = data.model_dump(exclude={"contact_methods"})
    contact = Contact(**payload)
    contact.contact_methods = [
        ContactMethod(**method.model_dump(exclude={"id"})) for method in data.contact_methods
    ]
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return get_contact(db, contact.id)


def update_contact(db: Session, contact_id: int, data: ContactUpdate) -> Contact:
    contact = get_contact(db, contact_id)
    for key, value in data.model_dump(exclude={"contact_methods"}).items():
        setattr(contact, key, value)

    existing = {method.id: method for method in contact.contact_methods}
    synchronized: list[ContactMethod] = []
    for method_data in data.contact_methods:
        if method_data.id is not None and method_data.id in existing:
            method = existing[method_data.id]
            method.type = method_data.type
            method.label = method_data.label
            method.value = method_data.value
            synchronized.append(method)
        else:
            synchronized.append(ContactMethod(**method_data.model_dump(exclude={"id"})))
    contact.contact_methods = synchronized
    db.commit()
    return get_contact(db, contact_id)


def delete_contact(db: Session, contact_id: int) -> None:
    contact = get_contact(db, contact_id)
    db.delete(contact)
    db.commit()


def set_favorite(db: Session, contact_id: int, is_favorite: bool) -> Contact:
    contact = get_contact(db, contact_id)
    contact.is_favorite = is_favorite
    db.commit()
    return get_contact(db, contact_id)


def get_stats(db: Session) -> dict:
    total = db.scalar(select(func.count(Contact.id))) or 0
    favorite = db.scalar(
        select(func.count(Contact.id)).where(Contact.is_favorite.is_(True))
    ) or 0
    phone = db.scalar(select(func.count(Contact.id)).where(
        Contact.contact_methods.any(ContactMethod.type == "phone")
    )) or 0
    email = db.scalar(select(func.count(Contact.id)).where(
        Contact.contact_methods.any(ContactMethod.type == "email")
    )) or 0
    recent = list(db.scalars(
        _base_query().order_by(Contact.created_at.desc(), Contact.id.desc()).limit(5)
    ).all())
    return {
        "total_contacts": total,
        "favorite_contacts": favorite,
        "contacts_with_phone": phone,
        "contacts_with_email": email,
        "recently_added": recent,
    }

