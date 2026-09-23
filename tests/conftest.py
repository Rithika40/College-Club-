import os
from pathlib import Path

TEST_DB = Path(__file__).resolve().parent.parent / "data" / "test.db"
os.environ["CCMS_DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
TEST_DB.parent.mkdir(parents=True, exist_ok=True)
if TEST_DB.exists():
    TEST_DB.unlink()
