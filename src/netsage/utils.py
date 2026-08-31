"""Shared utilities for NetSage AI modules."""

import csv
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# CSV utilities
def read_csv_dict(path: Path, encoding: str = "utf-8") -> Tuple[List[str], List[Dict[str, str]]]:
    """Read CSV file and return (fieldnames, rows). Returns ([], []) if file not found."""
    try:
        with path.open(newline="", encoding=encoding) as file:
            reader = csv.DictReader(file)
            return reader.fieldnames or [], list(reader)
    except FileNotFoundError:
        return [], []


def write_csv_dict(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str], encoding: str = "utf-8") -> None:
    """Write list of dicts to CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding=encoding) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_csv_rows(path: Path, rows: List[List[Any]], header: List[str], encoding: str = "utf-8") -> None:
    """Write list of lists to CSV file with header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding=encoding) as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


# Validation utilities
def validate_required_fields(row: Dict[str, str], required: List[str], row_num: int, file_name: str) -> List[str]:
    """Validate that required fields are not empty."""
    errors = []
    for field in required:
        if not row.get(field, "").strip():
            errors.append(f"{file_name}:{row_num}: {field} must not be empty")
    return errors


def validate_enum_value(value: str, valid_values: set, field_name: str, row_num: int, file_name: str) -> List[str]:
    """Validate that a value is in the allowed set."""
    if value not in valid_values:
        return [f"{file_name}:{row_num}: invalid {field_name} {value!r}"]
    return []


def validate_unique_values(values: List[str], value_name: str, file_name: str) -> List[str]:
    """Validate that all values in a list are unique."""
    if len(values) != len(set(values)):
        return [f"{file_name}: {value_name} values must be unique"]
    return []


# Path utilities
def ensure_dir(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)


# Error/Warning reporting
def print_error(message: str) -> None:
    """Print error message to stderr."""
    print(f"[X] {message}", file=sys.stderr)


def print_warning(message: str) -> None:
    """Print warning message to stderr."""
    print(f"[!] {message}", file=sys.stderr)


def print_info(message: str) -> None:
    """Print info message to stdout."""
    print(f"[+] {message}")


def print_ok(message: str) -> None:
    """Print success message to stdout."""
    print(f"[OK] {message}")


def print_progress(message: str) -> None:
    """Print progress message to stdout."""
    print(f"[*] {message}")


# Regex utilities
IP_PATTERN = re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b")
NETWORK_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}\b")


def find_ips(text: str) -> List[str]:
    """Find all IP addresses in text."""
    return IP_PATTERN.findall(text)


def find_networks(text: str) -> List[str]:
    """Find all network CIDR notations in text."""
    return NETWORK_PATTERN.findall(text)


# JSON utilities
def safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    """Safely parse JSON, return None on failure."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def extract_json_object(text: str) -> Optional[str]:
    """Extract first JSON object from text (handles markdown fences)."""
    match = re.search(r"\{.*\}", text, re.S)
    return match.group(0) if match else None