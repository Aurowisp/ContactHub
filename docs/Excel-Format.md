# Excel format

## Worksheet and base columns

The workbook must contain a worksheet named `Contacts`. `Name` is the only required base column. Supported base headers are `Name`, `Company`, `Job Title`, `Category`, `Notes`, and `Favorite`. Favorite accepts Yes/No, True/False, 1/0, or an empty value.

## Dynamic method columns

Each method uses a matched numbered pair:

```text
Phone 1 Label | Phone 1 Value | Phone 2 Label | Phone 2 Value
Email 1 Label | Email 1 Value
Social 1 Label | Social 1 Value
Address 1 Label | Address 1 Value
Website 1 Label | Website 1 Value
Other 1 Label | Other 1 Value
```

All six types may be repeated with positive sequence numbers. A populated method must have both its label and value. Unsupported headers, duplicate headers, and unmatched Label/Value pairs invalidate the workbook so data is never silently discarded.

## Import rules

- Files must be valid `.xlsx` workbooks no larger than 10 MB.
- Empty rows are counted as skipped; rows missing Name are errors.
- Valid rows commit even when other rows fail.
- Import is additive. It neither deletes nor deduplicates existing data, so repeated imports can create duplicates.
- Every row error includes the original worksheet row number and reason.
- Both exported workbooks and the downloadable template can be imported.

## Export rules

- One database contact occupies exactly one worksheet row.
- The maximum method count for each type determines its number of columns.
- Types, labels, values, favorite status, and all base information are preserved.
- IDs are intentionally excluded.
- Header filters, frozen panes, readable widths, and the `Contacts` name are applied.
- Text starting with `=`, `+`, `-`, or `@` is escaped to prevent spreadsheet formula injection.

