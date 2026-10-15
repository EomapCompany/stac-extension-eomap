import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


@pytest.fixture(scope="session")
def schema() -> dict:
    return load("json-schema/schema.json")
