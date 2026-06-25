"""Validation helpers for AI responses."""

from __future__ import annotations

import json
from typing import Any

from .exceptions import AIValidationError


class AIResponseValidator:
    """Validate AI JSON responses before parsing."""

    def validate_json_object(
        self,
        text: str,
        required_fields: tuple[str, ...],
        allowed_kinds: tuple[str, ...],
        allowed_keys: tuple[str, ...] = ("kind", "title", "summary", "items", "metadata"),
    ) -> dict[str, Any]:
        """Validate response text and return a JSON object."""
        if not text.strip():
            raise AIValidationError("AI response is empty")

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise AIValidationError(f"AI response is not valid JSON: {exc}") from exc

        if not isinstance(data, dict):
            raise AIValidationError("AI response must be a JSON object")

        unknown = sorted(set(data) - set(allowed_keys))
        if unknown:
            raise AIValidationError(f"AI response contains unknown keys: {unknown}")

        missing = [field for field in required_fields if field not in data]
        if missing:
            raise AIValidationError(f"AI response missing required fields: {missing}")

        if "kind" in data and data["kind"] not in allowed_kinds:
            raise AIValidationError(f"AI response has invalid kind: {data['kind']}")

        if "items" in data and not isinstance(data["items"], list):
            raise AIValidationError("AI response field 'items' must be a list")

        for field in ("kind", "title", "summary"):
            if field in data and not str(data[field]).strip():
                raise AIValidationError(f"AI response field '{field}' cannot be empty")

        return data
