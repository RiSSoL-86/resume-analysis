import logging
from typing import TYPE_CHECKING, Any, final, override

from django.conf import settings
from openai import AsyncOpenAI

from apps.common.services.base import BaseService
from services.analyzer.analysis.open_ai.prompt import (
    SYSTEM_PROMPT,
    build_user_input,
)
from services.analyzer.analysis.schemas import ResumeAnalysis

if TYPE_CHECKING:
    from openai.types.responses.response_usage import ResponseUsage

    from services.analyzer.schemas import CareerFacts

logger = logging.getLogger(__name__)


@final
class AnalyzerOpenAiService(BaseService):
    """Run the resume analysis with one structured LLM call."""

    def __init__(self) -> None:
        """Build the OpenAI client from project settings."""
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,  # type: ignore[misc]
        )
        self.model: str = settings.ANALYZER_LLM_MODEL  # type: ignore[misc]

    @override
    async def execute(
        self, dossier: dict[str, Any], computed_facts: CareerFacts
    ) -> ResumeAnalysis:
        """Return the parsed analysis for the dossier and facts."""
        user_input = build_user_input(
            dossier=dossier, computed_facts=computed_facts
        )
        response = await self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            text_format=ResumeAnalysis,
        )
        self._log_usage(response.usage)
        result = response.output_parsed
        if result is None:
            raise ValueError("Analyzer LLM returned no parsed result")
        return result

    def _log_usage(self, usage: ResponseUsage | None) -> None:
        """Log the OpenAI token spend for this analysis call."""
        if usage is None:
            return
        logger.info(
            msg=(
                f"OpenAI usage [{self.model}]: "
                f"input={usage.input_tokens}, "
                f"output={usage.output_tokens}, "
                f"total={usage.total_tokens} tokens"
            )
        )
