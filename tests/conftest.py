import datetime as dt
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"
RAW = ROOT / "data" / "raw"
TODAY = dt.date(2026, 11, 24)


@pytest.fixture
def today():
    return TODAY
