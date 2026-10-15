import re

import pytest
from conftest import load
from jsonschema import Draft7Validator

VOCABULARIES = ["products", "sensors", "vertical-datums"]


def normalize(name: str) -> str:
    """The matching rule documented in the README: case and non-alphanumerics are ignored."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


@pytest.mark.parametrize("name", VOCABULARIES)
def test_vocabulary_matches_its_schema(name):
    schema = load(f"vocabulary/{name}.schema.json")
    Draft7Validator.check_schema(schema)

    assert [e.message for e in Draft7Validator(schema).iter_errors(load(f"vocabulary/{name}.json"))] == []


@pytest.mark.parametrize("name", VOCABULARIES)
def test_ids_and_aliases_are_unambiguous(name):
    owners: dict[str, str] = {}
    for entry_id, entry in load(f"vocabulary/{name}.json").items():
        for alias in [entry_id, entry.get("title", ""), *entry.get("aliases", [])]:
            key = normalize(alias)
            assert owners.setdefault(key, entry_id) == entry_id, f"{alias!r}: {owners[key]} and {entry_id}"


def test_example_values_come_from_the_vocabulary():
    item = load("examples/item.json")
    products = load("vocabulary/products.json")
    sensors = load("vocabulary/sensors.json")
    datums = load("vocabulary/vertical-datums.json")

    assert set(item["properties"]["eomap:products"]) <= set(products)
    assert set(item["properties"]["eomap:sensors"]) <= set(sensors)
    assert item["assets"]["sdb"]["eomap:vertical_datum"] in datums


@pytest.mark.parametrize(
    ("spelling", "sensor"),
    [("Sentinel-2", "sn2"), ("SENT2", "sn2"), ("GeoEye1", "ge1"), ("WorldView-Legion", "wvl"), ("Spot-6", "sp6")],
)
def test_known_spellings_resolve(spelling, sensor):
    sensors = load("vocabulary/sensors.json")
    matches = [
        i
        for i, e in sensors.items()
        if normalize(spelling) in {normalize(a) for a in [i, e["title"], *e.get("aliases", [])]}
    ]

    assert matches == [sensor]
