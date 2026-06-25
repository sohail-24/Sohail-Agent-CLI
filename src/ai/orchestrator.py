"""Reusable AI orchestration pipeline."""

from __future__ import annotations

from src.providers import BaseProvider, GenerationRequest

from .exceptions import AIProviderError, AIValidationError
from .models import AIExecutionMetadata, AIRequest, AIResult
from .prompts import PromptBuilder
from .provider import AIProviderFactory, ProviderSpec
from .response_parser import AIResponseParser
from .router import AIRouter
from .validator import AIResponseValidator


class AIOrchestrator:
    """
    Deterministic controller for AI inference.

    Python owns routing, prompts, validation, retries, parsing, and returned
    dataclasses. Providers only return text.
    """

    def __init__(
        self,
        provider: BaseProvider | None = None,
        provider_spec: ProviderSpec | None = None,
        router: AIRouter | None = None,
        prompt_builder: PromptBuilder | None = None,
        validator: AIResponseValidator | None = None,
        parser: AIResponseParser | None = None,
    ) -> None:
        self.provider = AIProviderFactory().create(provider_spec, provider)
        self.router = router or AIRouter()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.validator = validator or AIResponseValidator()
        self.parser = parser or AIResponseParser()

    async def execute(self, request: AIRequest) -> AIResult:
        """Run the complete AI orchestration pipeline."""
        routed = self.router.route(request)
        if routed.prompt_name is None:
            raise AIProviderError("AI request has no prompt route")

        template, prompt = self.prompt_builder.build(
            routed.prompt_name,
            context=routed.context,
            instruction=routed.instruction,
        )
        attempts = 0
        last_error: Exception | None = None

        for attempts in range(1, routed.max_retries + 2):
            result = await self.provider.generate(
                GenerationRequest(
                    prompt=prompt,
                    model=routed.model,
                    system=template.system,
                    temperature=0.2,
                    options={"format": "json"},
                )
            )
            if not result.success:
                last_error = AIProviderError(result.error or "Provider failed")
                continue

            try:
                data = self.validator.validate_json_object(
                    result.text,
                    required_fields=routed.required_fields,
                    allowed_kinds=routed.allowed_kinds,
                )
                output = self.parser.parse_structured_output(data)
                return AIResult(
                    output=output,
                    metadata=AIExecutionMetadata(
                        provider=self.provider.name,
                        prompt_name=template.name,
                        prompt_version=template.version,
                        attempts=attempts,
                        model=result.model,
                    ),
                )
            except AIValidationError as exc:
                last_error = exc

        raise AIValidationError(
            f"AI response failed validation after {attempts} attempts: {last_error}"
        )
