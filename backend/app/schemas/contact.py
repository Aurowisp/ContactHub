from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ContactMethodType = Literal["phone", "email", "social", "address", "website", "other"]


class ContactMethodBase(BaseModel):
    type: ContactMethodType
    label: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=500)

    @field_validator("label", "value")
    @classmethod
    def strip_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


class ContactMethodCreate(ContactMethodBase):
    id: int | None = None


class ContactMethodRead(ContactMethodBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ContactBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    company: str | None = Field(default=None, max_length=200)
    job_title: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    is_favorite: bool = False
    contact_methods: list[ContactMethodCreate] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Contact name is required")
        return value

    @field_validator("company", "job_title", "category", "notes", mode="before")
    @classmethod
    def empty_to_none(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactRead(ContactBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    contact_methods: list[ContactMethodRead]


class ContactList(BaseModel):
    items: list[ContactRead]
    total: int
    skip: int
    limit: int


class FavoriteUpdate(BaseModel):
    is_favorite: bool


class ImportErrorItem(BaseModel):
    row: int
    reason: str


class ImportResult(BaseModel):
    total: int
    success: int
    skipped: int
    errors: list[ImportErrorItem]


class StatsResponse(BaseModel):
    total_contacts: int
    favorite_contacts: int
    contacts_with_phone: int
    contacts_with_email: int
    recently_added: list[ContactRead]

