"""Timestamp schema metadata must survive its ProtoJSON string serializer."""

import datetime

import pytest
from api.v1._proto_types import ProtoTimestamp
from api.v1.known_types_pydantic import WellKnownTypes
from pydantic import BaseModel, TypeAdapter


@pytest.mark.parametrize("mode", ["validation", "serialization"])
def test_timestamp_adapter_schema(mode):
    assert TypeAdapter(ProtoTimestamp).json_schema(mode=mode) == {
        "type": "string",
        "format": "date-time",
    }


@pytest.mark.parametrize("mode", ["validation", "serialization"])
def test_generated_timestamp_field_schema(mode):
    schema = WellKnownTypes.model_json_schema(mode=mode, by_alias=False)
    timestamp = schema["properties"]["wkt_timestamp"]
    assert {"type": "string", "format": "date-time"} in timestamp["anyOf"]


@pytest.mark.parametrize("mode", ["validation", "serialization"])
def test_required_timestamp_field_schema(mode):
    class Event(BaseModel):
        occurred: ProtoTimestamp

    schema = Event.model_json_schema(mode=mode)
    assert schema["properties"]["occurred"] == {
        "title": "Occurred",
        "type": "string",
        "format": "date-time",
    }
    assert schema["required"] == ["occurred"]


def test_timestamp_json_serialization_is_unchanged():
    adapter = TypeAdapter(ProtoTimestamp)
    value = datetime.datetime(2024, 1, 1, 12, 30, tzinfo=datetime.timezone.utc)
    encoded = adapter.dump_json(value)
    assert encoded == b'"2024-01-01T12:30:00Z"'
    assert adapter.validate_json(encoded) == value
