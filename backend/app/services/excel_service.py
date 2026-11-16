import io
import re
from collections import Counter, defaultdict

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.contact import Contact, ContactMethod
from app.schemas.contact import ContactCreate, ContactMethodCreate


METHOD_TYPES = ("phone", "email", "social", "address", "website", "other")
BASE_HEADERS = ["Name", "Company", "Job Title", "Category", "Notes", "Favorite"]
METHOD_HEADER_RE = re.compile(
    r"^(Phone|Email|Social|Address|Website|Other)\s+(\d+)\s+(Label|Value)$",
    re.IGNORECASE,
)
MAX_UPLOAD_SIZE = 10 * 1024 * 1024


def safe_excel_value(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value)
    if text.startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def _style_workbook(workbook: Workbook, worksheet) -> None:
    header_fill = PatternFill("solid", fgColor="1677FF")
    for cell in worksheet[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = header_fill
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions
    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        worksheet.column_dimensions[get_column_letter(column_cells[0].column)].width = min(
            max(max_length + 2, 12), 45
        )


def export_contacts(db: Session) -> bytes:
    contacts = list(db.scalars(
        select(Contact).options(selectinload(Contact.contact_methods)).order_by(Contact.id)
    ).all())
    maxima = Counter({method_type: 1 for method_type in METHOD_TYPES})
    for contact in contacts:
        counts = Counter(method.type for method in contact.contact_methods)
        for method_type, count in counts.items():
            maxima[method_type] = max(maxima[method_type], count)

    headers = list(BASE_HEADERS)
    for method_type in METHOD_TYPES:
        for index in range(1, maxima[method_type] + 1):
            title = method_type.title()
            headers.extend([f"{title} {index} Label", f"{title} {index} Value"])

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Contacts"
    worksheet.append(headers)
    for contact in contacts:
        row = [
            safe_excel_value(contact.name), safe_excel_value(contact.company),
            safe_excel_value(contact.job_title), safe_excel_value(contact.category),
            safe_excel_value(contact.notes), "Yes" if contact.is_favorite else "No",
        ]
        grouped = defaultdict(list)
        for method in contact.contact_methods:
            grouped[method.type].append(method)
        for method_type in METHOD_TYPES:
            for index in range(maxima[method_type]):
                if index < len(grouped[method_type]):
                    method = grouped[method_type][index]
                    row.extend([safe_excel_value(method.label), safe_excel_value(method.value)])
                else:
                    row.extend(["", ""])
        worksheet.append(row)
    _style_workbook(workbook, worksheet)
    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def create_template() -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Contacts"
    headers = list(BASE_HEADERS)
    for method_type in METHOD_TYPES:
        headers.extend([f"{method_type.title()} 1 Label", f"{method_type.title()} 1 Value"])
    worksheet.append(headers)
    example = ["Zhang San", "ABC Technology", "Engineer", "Work", "Example row", "Yes"]
    examples = {
        "phone": ("Mobile", "13800000000"), "email": ("Work", "zhang@example.com"),
        "social": ("WeChat", "zhangsan123"), "address": ("Home", "Fuzhou, China"),
        "website": ("Portfolio", "https://example.com"), "other": ("Telegram", "@zhang"),
    }
    for method_type in METHOD_TYPES:
        example.extend(examples[method_type])
    worksheet.append(example)
    _style_workbook(workbook, worksheet)
    instructions = workbook.create_sheet("Instructions")
    instructions.append(["ContactHub Excel Import Instructions"])
    instructions.append(["Name is required. All other base fields are optional."])
    instructions.append(["Favorite accepts Yes/No, True/False, 1/0."])
    instructions.append(["Add numbered Label/Value column pairs to include multiple methods."])
    instructions.append(["A method must have both a non-empty label and value."])
    instructions.append(["Repeated imports are additive and may create duplicate contacts."])
    instructions.column_dimensions["A"].width = 85
    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def _cell_text(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if len(text) > 1 and text[0] == "'" and text[1] in ("=", "+", "-", "@"):
        return text[1:]
    return text


def import_contacts(db: Session, content: bytes) -> dict:
    try:
        workbook = load_workbook(io.BytesIO(content), data_only=False)
    except Exception as exc:
        raise ValueError("The uploaded file is not a valid .xlsx workbook") from exc
    if "Contacts" not in workbook.sheetnames:
        raise ValueError("Workbook must contain a 'Contacts' worksheet")
    worksheet = workbook["Contacts"]
    headers = [_cell_text(cell.value) for cell in worksheet[1]]
    if not headers or "Name" not in headers:
        raise ValueError("Missing required column: Name")
    if len(headers) != len(set(headers)):
        raise ValueError("Duplicate column headers are not allowed")
    base_indexes = {header: headers.index(header) for header in BASE_HEADERS if header in headers}
    method_columns: dict[tuple[str, int], dict[str, int]] = defaultdict(dict)
    unknown = []
    for index, header in enumerate(headers):
        if not header or header in BASE_HEADERS:
            continue
        match = METHOD_HEADER_RE.match(header)
        if not match:
            unknown.append(header)
            continue
        method_type, number, part = match.groups()
        method_columns[(method_type.lower(), int(number))][part.lower()] = index
    if unknown:
        raise ValueError(f"Unsupported column header(s): {', '.join(unknown)}")
    for key, parts in method_columns.items():
        if set(parts) != {"label", "value"}:
            raise ValueError(f"Incomplete method columns for {key[0].title()} {key[1]}")

    total = success = skipped = 0
    errors = []
    for row_number, cells in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
        values = list(cells)
        if all(_cell_text(value) == "" for value in values):
            skipped += 1
            continue
        total += 1
        try:
            name = _cell_text(values[base_indexes["Name"]])
            if not name:
                raise ValueError("Missing contact name")
            favorite_raw = _cell_text(values[base_indexes["Favorite"]]).lower() if "Favorite" in base_indexes else ""
            if favorite_raw in {"yes", "true", "1", "y"}:
                favorite = True
            elif favorite_raw in {"", "no", "false", "0", "n"}:
                favorite = False
            else:
                raise ValueError("Favorite must be Yes/No, True/False, or 1/0")
            methods = []
            for (method_type, _number), indexes in sorted(method_columns.items()):
                label = _cell_text(values[indexes["label"]] if indexes["label"] < len(values) else None)
                value = _cell_text(values[indexes["value"]] if indexes["value"] < len(values) else None)
                if bool(label) != bool(value):
                    raise ValueError(f"{method_type.title()} method requires both label and value")
                if label and value:
                    methods.append(ContactMethodCreate(type=method_type, label=label, value=value))
            def optional(header: str) -> str | None:
                if header not in base_indexes:
                    return None
                text = _cell_text(values[base_indexes[header]])
                return text or None
            data = ContactCreate(
                name=name, company=optional("Company"), job_title=optional("Job Title"),
                category=optional("Category"), notes=optional("Notes"),
                is_favorite=favorite, contact_methods=methods,
            )
            with db.begin_nested():
                contact = Contact(**data.model_dump(exclude={"contact_methods"}))
                contact.contact_methods = [
                    ContactMethod(**method.model_dump(exclude={"id"}))
                    for method in data.contact_methods
                ]
                db.add(contact)
                db.flush()
            db.commit()
            success += 1
        except Exception as exc:
            db.rollback()
            errors.append({"row": row_number, "reason": str(exc)})
    return {"total": total, "success": success, "skipped": skipped, "errors": errors}

