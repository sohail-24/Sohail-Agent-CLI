import pytest

from src.ai.exceptions import AIValidationError
from src.ai.validator import AIResponseValidator


def test_validator_accepts_valid_json_object():
    data = AIResponseValidator().validate_json_object(
        '{"kind":"planning","title":"Plan","summary":"Summary","items":["a"],"metadata":{}}',
        required_fields=("kind", "title", "summary", "items"),
        allowed_kinds=("planning",),
    )
    assert data["kind"] == "planning"


@pytest.mark.parametrize(
    "text,match",
    [
        ("", "empty"),
        ("not json", "valid JSON"),
        ('["not-object"]', "JSON object"),
        ('{"kind":"planning","title":"Plan","summary":"Summary","items":[],"extra":1}', "unknown"),
        ('{"kind":"planning","title":"Plan","items":[]}', "missing"),
        ('{"kind":"other","title":"Plan","summary":"Summary","items":[]}', "invalid kind"),
        ('{"kind":"planning","title":"Plan","summary":"Summary","items":"bad"}', "must be a list"),
    ],
)
def test_validator_rejects_invalid_responses(text, match):
    with pytest.raises(AIValidationError, match=match):
        AIResponseValidator().validate_json_object(
            text,
            required_fields=("kind", "title", "summary", "items"),
            allowed_kinds=("planning",),
        )
