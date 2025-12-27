from pathlib import Path

def get_config():
    return {
        "env": "dev",
        "data_path": Path("data/customer.csv"),
        "log_level": "INFO",
        "fail_on_invalid": False
    }
