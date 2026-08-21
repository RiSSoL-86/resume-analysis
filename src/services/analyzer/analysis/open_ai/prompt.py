import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from services.analyzer.schemas import CareerFacts

ANALYSIS_DIR: Final[Path] = Path(__file__).resolve().parent.parent
PROMPTS_DIR: Final[Path] = ANALYSIS_DIR / "prompts"
RULES_DIR: Final[Path] = ANALYSIS_DIR / "rules"
KNOWLEDGE_DIR: Final[Path] = ANALYSIS_DIR / "knowledge"


def read_asset(path: Path) -> str:
    """Read a UTF-8 prompt asset shipped with the package."""
    return path.read_text(encoding="utf-8")


SYSTEM_PROMPT: Final[str] = read_asset(
    PROMPTS_DIR / "analyze_resume.system.md"
)
UNIVERSAL_RULES: Final[str] = read_asset(RULES_DIR / "universal.yaml")
# Role-relevance rules: profession-agnostic guidance for judging skills
# relative to the candidate's inferred target role (no per-role config).
ROLE_RELEVANCE_RULES: Final[str] = read_asset(
    RULES_DIR / "role_relevance.yaml"
)
# Expert knowledge documents, in the order the model should read them.
KNOWLEDGE_DOCUMENTS: Final[tuple[tuple[str, str], ...]] = (
    ("company_signals", read_asset(KNOWLEDGE_DIR / "company_signals.yaml")),
    ("career_signals", read_asset(KNOWLEDGE_DIR / "career_signals.yaml")),
    ("level_thresholds", read_asset(KNOWLEDGE_DIR / "level_thresholds.yaml")),
)


def build_user_input(
    dossier: dict[str, Any], computed_facts: CareerFacts
) -> str:
    """Assemble the user message: rules, knowledge, facts and dossier."""
    facts_json = json.dumps(
        computed_facts.model_dump(by_alias=True),
        ensure_ascii=False,
        indent=2,
    )
    dossier_json = json.dumps(dossier, ensure_ascii=False, indent=2)
    sections = [
        "# Универсальные HR-правила\n" + UNIVERSAL_RULES,
        "# Правила оценки относительно роли\n" + ROLE_RELEVANCE_RULES,
        *(
            f"# Экспертная база: {name}\n{content}"
            for name, content in KNOWLEDGE_DOCUMENTS
        ),
        "# Авторитетные вычисленные факты\n```json\n" + facts_json + "\n```",
        "# Данные кандидата и резюме\n```json\n" + dossier_json + "\n```",
    ]
    return "\n\n".join(sections)
