import copy
import re

import pytest
import stac_pydantic
from conftest import ROOT, load
from jsonschema import Draft7Validator, FormatChecker


def errors(schema: dict, document: dict) -> list[str]:
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    return [error.message for error in validator.iter_errors(document)]


def test_schema_is_valid_draft7(schema):
    Draft7Validator.check_schema(schema)


@pytest.mark.parametrize("example", ["examples/item.json", "examples/collection.json"])
def test_examples_validate(schema, example):
    assert errors(schema, load(example)) == []


def test_examples_are_valid_stac():
    stac_pydantic.Item.model_validate(load("examples/item.json"))
    stac_pydantic.Collection.model_validate(load("examples/collection.json"))


def with_property(**fields) -> dict:
    item = copy.deepcopy(load("examples/item.json"))
    item["properties"].update(fields)
    return item


@pytest.mark.parametrize(
    "fields",
    [
        {"eomap:unknown": 1},
        {"eomap:country_code": "JM"},
        {"eomap:products": ["sdb"]},
        {"eomap:products": []},
        {"eomap:corrections": ["sunglint"]},
        {"eomap:access": ["customer-a"]},
        {"eomap:source": "ftp"},
        {"eomap:horizontal_accuracy": -1},
        {"eomap:tide_stations": [{"number": "2491"}]},
        {"eomap:access": ["user#bob\n"]},
        {"eomap:access": ["role#x:y z"]},
        {"eomap:products": ["SDB-"]},
        {"eomap:country_code": "JAM\n"},
    ],
    ids=lambda fields: next(iter(fields)),
)
def test_invalid_fields_are_rejected(schema, fields):
    assert errors(schema, with_property(**fields))


def test_unknown_fields_on_assets_are_rejected(schema):
    item = copy.deepcopy(load("examples/item.json"))
    item["assets"]["sdb"]["eomap:typo"] = "x"

    assert errors(schema, item)


def test_extension_must_be_declared(schema):
    item = copy.deepcopy(load("examples/item.json"))
    item["stac_extensions"] = []

    assert errors(schema, item)


def test_version_is_consistent():
    schema_id = load("json-schema/schema.json")["$id"]
    version = re.search(r"/v(\d+\.\d+\.\d+)/schema\.json$", schema_id)[1]
    changelog = (ROOT / "CHANGELOG.md").read_text()

    assert re.search(r"^## \[v(\d+\.\d+\.\d+)\]", changelog, re.M)[1] == version
    for example in ["examples/item.json", "examples/collection.json"]:
        assert schema_id in load(example)["stac_extensions"]


def with_collection(**fields) -> dict:
    collection = copy.deepcopy(load("examples/collection.json"))
    collection.update(fields)
    return collection


@pytest.mark.parametrize(
    "fields",
    [
        {"eomap:project_date": "2026-13-45"},
        {"eomap:unknown": 1},
        {"eomap:access": ["nobody"]},
        {"summaries": {"eomap:products": ["sdb"]}},
        {"summaries": {"eomap:typo": ["x"]}},
    ],
    ids=lambda fields: next(iter(fields)),
)
def test_invalid_collection_fields_are_rejected(schema, fields):
    assert errors(schema, with_collection(**fields))


def test_eomap_fields_belong_into_item_properties(schema):
    item = copy.deepcopy(load("examples/item.json"))
    item["eomap:products"] = ["SDB"]

    assert errors(schema, item)


def test_any_eomap_field_satisfies_the_extension(schema):
    item = copy.deepcopy(load("examples/item.json"))
    item["properties"] = {"datetime": item["properties"]["datetime"]}  # eomap fields only on assets

    assert errors(schema, item) == []


def test_declaring_the_extension_without_any_field_is_invalid(schema):
    item = copy.deepcopy(load("examples/item.json"))
    item["properties"] = {"datetime": item["properties"]["datetime"]}
    item["assets"] = {"data": {"href": "https://example.org/x.tif"}}

    assert errors(schema, item)
