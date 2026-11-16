"""Shared domain validation helpers."""

from tutoring.domain.exceptions import ValidationError


def require_non_empty(value: str, field_name: str) -> str:
    """Validate that a string is non-empty after stripping whitespace."""
    normalized = value.strip()
    if not normalized:
        raise ValidationError(f"Field '{field_name}' cannot be empty.")
    return normalized
