from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    env: str
    data_path: Path
    log_level: str
    show_invalid_rows: bool
    max_invalid_pct: float

def get_config(env: str = "dev") -> Config:
    if env == "prod":
        return Config(
            env="prod",
            data_path= Path("data/customer.csv"),
            log_level="WARNING",
            show_invalid_rows=False,
            max_invalid_pct=20.0
        )

    # dev (default)
    return Config(
        env="dev",
        data_path=Path("data/customer.csv"),
        log_level="INFO",
        show_invalid_rows=True,
        max_invalid_pct=50.0
    )

