import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("MEDIASSIST_DB_PATH", str(Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "nonexistent.db"))
os.environ.setdefault("MEDIASSIST_DATA_PATH", str(Path(__file__).resolve().parents[1] / "tests" / "fixtures"))

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
