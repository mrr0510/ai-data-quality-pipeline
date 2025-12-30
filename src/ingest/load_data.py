import csv
import os
import json
import logging
from pathlib import Path

from src.config.settings import get_config

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


def build_metrics(env: str, total: int, valid: int, invalid: int) -> dict:
    invalid_pct = (invalid / total * 100) if total > 0 else 0

    return {
        "environment": env,
        "total_rows": total,
        "valid_rows": valid,
        "invalid_rows": invalid,
        "invalid_percentage": round(invalid_pct, 2),
    }


def main():
    env = os.getenv("APP_ENV", "dev")
    config = get_config(env)

    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    logger = logging.getLogger(__name__)

    logger.info("Starting customer CSV ingestion")

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

    logger.info("Valid rows: %d", len(valid_rows))
    logger.warning("Invalid rows: %d", len(invalid_rows))

    # Metrics
    metrics = build_metrics(
        env=env,
        total=len(rows),
        valid=len(valid_rows),
        invalid=len(invalid_rows),
    )

    metrics_path = Path("output/metrics/quality_metrics.json")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info("Quality metrics written to %s", metrics_path)

    # =========================
    # QUALITY GATE (FIXED PLACE)
    # =========================
    invalid_pct = (
        len(invalid_rows) / len(rows) * 100
        if rows else 0
    )

    logger.info(
        "Invalid data percentage: %.2f%% (threshold: %.2f%%)",
        invalid_pct,
        config.max_invalid_pct
    )

    if invalid_pct > config.max_invalid_pct:
        message = (
            f"Data quality gate failed: "
            f"{invalid_pct:.2f}% invalid rows "
            f"(threshold {config.max_invalid_pct}%)"
        )

        if config.env == "prod":
            logger.error(message)
            raise RuntimeError(message)
        else:
            logger.warning(message)

    # DEV-only visibility
    if config.show_invalid_rows:
        for item in invalid_rows:
            logger.warning("Invalid row detail: %s", item)

    logger.info("Ingestion completed successfully")


if __name__ == "__main__":
    main()
