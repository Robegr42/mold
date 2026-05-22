import pytest
from typing import Dict
from gensie.baseline import compress_schema_to_ts

def test_compress_schema_to_ts_basic():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "score": {"type": "number"}
        },
        "required": ["name"]
    }
    
    expected_ts = "{ name: string; age?: number; score?: number; }"
    # Or maybe it will be formatted with newlines. Let's assume a one-liner or minimal whitespace
    # Let's define expected behavior:
    # Optional fields get `?`
    # types: string -> string, integer -> number, number -> number
    
    result = compress_schema_to_ts(schema)
    
    # We can remove whitespace for easier comparison if we want, or define an exact format
    assert "".join(result.split()) == "".join(expected_ts.split())

def test_compress_schema_to_ts_nested():
    schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        }
    }
    expected_ts = "{ user?: { id: string; }; }"
    
    result = compress_schema_to_ts(schema)
    assert "".join(result.split()) == "".join(expected_ts.split())

def test_compress_schema_to_ts_array():
    schema = {
        "type": "object",
        "properties": {
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["tags"]
    }
    expected_ts = "{ tags: string[]; }"
    result = compress_schema_to_ts(schema)
    assert "".join(result.split()) == "".join(expected_ts.split())

def test_compress_schema_enum():
    schema = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["active", "inactive", "pending"]
            }
        }
    }
    result = compress_schema_to_ts(schema)
    assert '"active" | "inactive" | "pending"' in result

def test_compress_schema_description():
    schema = {
        "type": "object",
        "properties": {
            "count": {
                "type": "integer",
                "description": "Total number of items"
            }
        }
    }
    result = compress_schema_to_ts(schema)
    assert "Total number of items" in result

def test_compress_schema_format():
    schema = {
        "type": "object",
        "properties": {
            "created_at": {
                "type": "string",
                "format": "date-time"
            }
        }
    }
    result = compress_schema_to_ts(schema)
    assert "date-time" in result

def test_compress_schema_one_of():
    schema = {
        "type": "object",
        "properties": {
            "value": {
                "oneOf": [
                    {"type": "string"},
                    {"type": "number"}
                ]
            }
        }
    }
    result = compress_schema_to_ts(schema)
    assert "string" in result
    assert "number" in result
    assert "|" in result

def test_compress_schema_with_ref():
    schema = {
        "$defs": {
            "Address": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                }
            }
        },
        "type": "object",
        "properties": {
            "address": {"$ref": "#/$defs/Address"}
        }
    }
    result = compress_schema_to_ts(schema)
    assert "city" in result
