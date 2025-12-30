import csv
import os
from pathlib import Path
import logging
from src.config.settings import get_config


REQUIRED_COLUMNS = {"customer_id", "name", "age", "email", "country"}


logger = logging.getLogger(__name__)



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

logger.info("Starting customer CSV ingestion")
def main():
    env = os.getenv("APP_ENV", "dev")
    config = get_config(env)
    logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s | %(levelname)s | %(message)s"
)
    data_path = config.data_path
    rows = load_csv(data_path)
    valid_rows = []
    invalid_rows = []

    for row in rows:
        errors = validate_row(row)
        if errors:
            invalid_rows.append({"row": row, "errors": errors})
        else:
            valid_rows.append(row)

    logger.info("Valid rows written: %d", len(valid_rows))
    logger.warning("Invalid rows written: %d", len(invalid_rows))

    if config.show_invalid_rows:
        for item in invalid_rows:
            print(item)
if __name__ == "__main__":
    main()

logger.info("Ingestion completed successfully")

