import copy
import re

import pytest
import stac_pydantic
from conftest import ROOT, load
from jsonschema import Draft7Validator


def errors(schema: dict, document: dict) -> list[str]:
    return [error.message for error in Draft7Validator(schema).iter_errors(document)]


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
