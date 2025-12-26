import csv
from pathlib import Path


REQUIRED_COLUMNS = {"customer_id", "name", "age", "email", "country"}


def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            raise ValueError("CSV schema mismatch")

        return list(reader)


def validate_row(row: dict) -> list[str]:
    errors = []

    if not row["name"]:
        errors.append("name is missing")

    try:
        age = int(row["age"])
        if age <= 0:
            errors.append("age must be positive")
    except ValueError:
        errors.append("age is not an integer")

    return errors


def main():
    data_path = Path("data/customer.csv")
    rows = load_csv(data_path)

    valid_rows = []
    invalid_rows = []

    for row in rows:
        errors = validate_row(row)
        if errors:
            invalid_rows.append({"row": row, "errors": errors})
        else:
            valid_rows.append(row)

    print(f"Valid rows: {len(valid_rows)}")
    print(f"Invalid rows: {len(invalid_rows)}")

    for item in invalid_rows:
        print(item)


if __name__ == "__main__":
    main()
