import os
from pathlib import Path
from typing import Optional


def load_environment(env_path: Optional[str] = None) -> None:
    """Load environment variables from a .env file, if present.

    If a .env file exists next to this module, its key/value pairs will be
    added to os.environ only when the variable is not already defined.
    """
    if env_path is None:
        env_path = Path(__file__).resolve().parent / ".env"
    else:
        env_path = Path(env_path)

    if not env_path.exists():
        return

    with env_path.open("r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and os.getenv(key) is None:
                os.environ[key] = value
