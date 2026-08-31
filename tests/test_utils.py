"""Tests for netsage.utils module."""

import json
from pathlib import Path

from netsage.utils import (
    read_csv_dict,
    write_csv_dict,
    write_csv_rows,
    validate_required_fields,
    validate_enum_value,
    validate_unique_values,
    ensure_dir,
    find_ips,
    find_networks,
    safe_json_loads,
    extract_json_object,
)


class TestUtils:
    def test_read_csv_dict_missing_file(self, tmp_path):
        columns, rows = read_csv_dict(tmp_path / "missing.csv")
        assert columns == []
        assert rows == []

    def test_write_and_read_csv_dict(self, tmp_path):
        path = tmp_path / "test.csv"
        rows = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
        write_csv_dict(path, rows, ["id", "name"])
        columns, read_rows = read_csv_dict(path)
        assert columns == ["id", "name"]
        assert read_rows == rows

    def test_write_csv_rows(self, tmp_path):
        path = tmp_path / "test.csv"
        write_csv_rows(path, [["1", "Alice"], ["2", "Bob"]], ["id", "name"])
        columns, rows = read_csv_dict(path)
        assert columns == ["id", "name"]
        assert len(rows) == 2

    def test_validate_required_fields(self):
        row = {"a": "1", "b": "", "c": "3"}
        errors = validate_required_fields(row, ["a", "b"], 5, "test.csv")
        assert len(errors) == 1
        assert "b must not be empty" in errors[0]

    def test_validate_enum_value(self):
        errors = validate_enum_value("invalid", {"valid", "ok"}, "field", 1, "test.csv")
        assert len(errors) == 1
        assert "invalid field" in errors[0]

        errors = validate_enum_value("valid", {"valid", "ok"}, "field", 1, "test.csv")
        assert errors == []

    def test_validate_unique_values(self):
        errors = validate_unique_values(["a", "b", "a"], "id", "test.csv")
        assert len(errors) == 1
        assert "id values must be unique" in errors[0]

        errors = validate_unique_values(["a", "b", "c"], "id", "test.csv")
        assert errors == []

    def test_ensure_dir(self, tmp_path):
        ensure_dir(tmp_path / "new" / "nested")
        assert (tmp_path / "new" / "nested").is_dir()

    def test_find_ips(self):
        text = "192.168.1.1 and 10.0.0.1"
        assert find_ips(text) == ["192.168.1.1", "10.0.0.1"]

    def test_find_networks(self):
        text = "192.168.1.0/24 and 10.0.0.0/8"
        assert find_networks(text) == ["192.168.1.0/24", "10.0.0.0/8"]

    def test_safe_json_loads(self):
        assert safe_json_loads('{"a": 1}') == {"a": 1}
        assert safe_json_loads("not json") is None

    def test_extract_json_object(self):
        text = 'some text {"key": "value"} more text'
        assert extract_json_object(text) == '{"key": "value"}'

        text = '```json\n{"a": 1}\n```'
        assert extract_json_object(text) == '{"a": 1}'