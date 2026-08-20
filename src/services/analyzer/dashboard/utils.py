import math
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from services.analyzer.dashboard.constants import (
    CURRENCY_SYMBOLS,
    DEPTH_LEVELS,
    EXPERIENCE_ATTENTION_MONTHS,
    EXPERIENCE_STRONG_MONTHS,
    GAP_ATTENTION_MONTHS,
    GAP_CRITICAL_MONTHS,
    JOB_FULL_YEAR_MONTHS,
    LEVEL_ATTENTION_RANK,
    LEVEL_RANKS,
    LEVEL_STRONG_RANK,
    MENTION_LEVEL_BANDS,
    MONTH_ABBR,
    OVERALL_ATTENTION,
    OVERALL_DOMAIN_BONUS,
    OVERALL_EXPERIENCE_FULL_MONTHS,
    OVERALL_EXPERIENCE_WEIGHT,
    OVERALL_LEVEL_WEIGHT,
    OVERALL_POSITIVE,
    OVERALL_SKILL_WEIGHT,
    RADAR_AXES,
    RADAR_CENTER,
    RADAR_RADIUS,
    RESUME_FRESH_MONTHS,
    RESUME_STALE_MONTHS,
    SEVERITY_STATUS,
    SKILL_MAX_LEVEL,
    SKILL_SCORE_ATTENTION,
    SKILL_SCORE_STRONG,
    TENURE_LEVEL_BANDS,
)
from services.analyzer.dashboard.schemas import SkillAxis

if TYPE_CHECKING:
    from services.analyzer.analysis.schemas import (
        EstimatedDepth,
        Risk,
        Status,
        Unknown,
    )

# Two Russian word forms are treated as the same topic when they share this
# many leading characters — a cheap stemmer that folds "причина"/"причины".
_STEM_LENGTH: int = 5
_MIN_TOKEN_LENGTH: int = 4
# Share of an unknown's stems that must also appear in a risk for the unknown
# to count as already covered by that risk.
_COVERAGE_THRESHOLD: float = 0.5


def compact_text(value: str | None, limit: int = 170) -> str:
    """Trim text to a single readable sentence within the limit."""
    text = " ".join((value or "").split())
    if len(text) <= limit:
        return text
    cut = text.rfind(". ", 0, limit)
    if cut >= 60:
        return text[: cut + 1]
    return text[: limit - 1].rstrip(" ,;:—-") + "…"


def _stems(text: str) -> set[str]:
    """Reduce free text to a set of leading-character word stems."""
    return {
        word[:_STEM_LENGTH]
        for word in re.findall(r"\w+", text.lower())
        if len(word) >= _MIN_TOKEN_LENGTH
    }


def prune_covered_unknowns(
    unknowns: list[Unknown], risks: list[Risk]
) -> list[Unknown]:
    """Drop unknowns whose subject is already spelled out by a risk."""
    risk_stems = [_stems(f"{risk.title} {risk.explanation}") for risk in risks]
    kept: list[Unknown] = []
    for unknown in unknowns:
        stems = _stems(unknown.subject)
        covered = any(
            stems and len(stems & hay) / len(stems) >= _COVERAGE_THRESHOLD
            for hay in risk_stems
        )
        if not covered:
            kept.append(unknown)
    return kept


def plural(value: int, forms: tuple[str, str, str]) -> str:
    """Pick the Russian plural form for a count."""
    if value % 10 == 1 and value % 100 != 11:
        return forms[0]
    if value % 10 in (2, 3, 4) and value % 100 not in (12, 13, 14):
        return forms[1]
    return forms[2]


def age_label(age: int | None) -> str:
    """Render the candidate's age, or a placeholder when it is unknown."""
    if age is None:
        return "Нет данных"
    return f"{age} {plural(age, ('год', 'года', 'лет'))}"


def salary_label(value: int | None, currency: str | None) -> str:
    """Render the salary expectation, or a placeholder when unstated."""
    if value is None or value <= 0:
        return "Не указана"
    amount = f"{value:,}".replace(",", " ")
    code = (currency or "").upper()
    symbol = CURRENCY_SYMBOLS.get(code)
    if symbol is not None:
        return f"{amount} {symbol}"
    return f"{amount} {code}".strip()


def _parse_date(value: str | None) -> datetime | None:
    """Parse an ISO date/datetime string into an aware UTC datetime."""
    if not value:
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        try:
            parsed = datetime.strptime(text[:10], "%Y-%m-%d")
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _months_since(value: str | None) -> int | None:
    """Whole months between an ISO date and now, or None if unparseable."""
    parsed = _parse_date(value)
    if parsed is None:
        return None
    now = datetime.now(UTC)
    months = (now.year - parsed.year) * 12 + (now.month - parsed.month)
    if now.day < parsed.day:
        months -= 1
    return max(0, months)


def updated_label(value: str | None) -> str | None:
    """Render the resume-update date as DD.MM.YYYY, or None if unknown."""
    parsed = _parse_date(value)
    if parsed is None:
        return None
    return parsed.strftime("%d.%m.%Y")


def updated_status(value: str | None) -> Status:
    """Freshness colour: under a month green, 1-3 yellow, older red."""
    months = _months_since(value)
    if months is None:
        return "unknown"
    if months < RESUME_FRESH_MONTHS:
        return "positive"
    if months < RESUME_STALE_MONTHS:
        return "attention"
    return "negative"


def duration_label(months: int | float | None) -> str:
    """Render a month count as a Russian years/months phrase."""
    if months is None:
        return "Не рассчитано"
    total = round(months)
    years, rest = divmod(total, 12)
    parts: list[str] = []
    if years:
        parts.append(f"{years} {plural(years, ('год', 'года', 'лет'))}")
    if rest or not parts:
        parts.append(f"{rest} {plural(rest, ('месяц', 'месяца', 'месяцев'))}")
    return " ".join(parts)


def month_year_label(month_index: int | None) -> str:
    """Render a months-since-year-0 point as ``июнь 2018``."""
    if month_index is None:
        return ""
    year, month = divmod(month_index, 12)
    return f"{MONTH_ABBR[month]} {year}"


def level_percent(level: str) -> float:
    """Map a seniority level onto a 0-100 component (unknown = 0)."""
    if level not in LEVEL_RANKS:
        return 0.0
    return LEVEL_RANKS.index(level) / (len(LEVEL_RANKS) - 1) * 100


def overall_score(
    skill_scores: list[int],
    level: str,
    total_months: int | None,
    domain_present: bool,
) -> int:
    """Blend must-have skills, seniority and tenure into a 0-100 rating."""
    skills_pct = (
        sum(skill_scores) / (len(skill_scores) * SKILL_MAX_LEVEL) * 100
        if skill_scores
        else 0.0
    )
    experience_pct = (
        min((total_months or 0) / OVERALL_EXPERIENCE_FULL_MONTHS, 1.0) * 100
    )
    score = (
        OVERALL_SKILL_WEIGHT * skills_pct
        + OVERALL_LEVEL_WEIGHT * level_percent(level)
        + OVERALL_EXPERIENCE_WEIGHT * experience_pct
    )
    if domain_present:
        score += OVERALL_DOMAIN_BONUS
    return max(0, min(100, round(score)))


def overall_status(score: int) -> Status:
    """Traffic-light colour for the overall candidate score."""
    if score >= OVERALL_POSITIVE:
        return "positive"
    if score >= OVERALL_ATTENTION:
        return "attention"
    return "negative"


def experience_status(total_months: int | None) -> Status:
    """Traffic-light colour for total experience: 5+ green, 3-5 yellow, red."""
    months = total_months or 0
    if months >= EXPERIENCE_STRONG_MONTHS:
        return "positive"
    if months >= EXPERIENCE_ATTENTION_MONTHS:
        return "attention"
    return "negative"


def level_status(level: str) -> Status:
    """Traffic-light colour for seniority: middle+ green, middle yellow."""
    if level not in LEVEL_RANKS:
        return "unknown"
    rank = LEVEL_RANKS.index(level)
    if rank >= LEVEL_RANKS.index(LEVEL_STRONG_RANK):
        return "positive"
    if rank >= LEVEL_RANKS.index(LEVEL_ATTENTION_RANK):
        return "attention"
    return "negative"


def skill_status(score: int) -> Status:
    """Traffic-light colour for a skill, consistent with its radar area."""
    if score >= SKILL_SCORE_STRONG:
        return "positive"
    if score >= SKILL_SCORE_ATTENTION:
        return "attention"
    return "negative"


def severity_status(severity: str) -> Status:
    """Traffic-light colour for a risk severity."""
    return SEVERITY_STATUS.get(severity, "neutral")  # type: ignore[return-value]


def education_item_status(technical: bool | None) -> Status:
    """Traffic-light colour for whether one education is technical."""
    if technical is True:
        return "positive"
    if technical is False:
        return "attention"
    return "unknown"


def band_level(value: int, bands: tuple[tuple[int, int], ...]) -> int:
    """Map a raw value onto an absolute 0-5 level via ordered bands."""
    for lower_bound, level in bands:
        if value >= lower_bound:
            return level
    return 0


def depth_level(depth: EstimatedDepth) -> int:
    """Map a skill's depth of ownership onto the absolute 0-5 level."""
    return DEPTH_LEVELS.get(depth, 0)


def skill_axes(
    mentions: int, tenure_months: int, depth: int
) -> list[SkillAxis]:
    """Build the three 0-5 radar axes: mentions, tenure, depth."""
    levels = (
        band_level(mentions, MENTION_LEVEL_BANDS),
        band_level(tenure_months, TENURE_LEVEL_BANDS),
        depth,
    )
    return [
        SkillAxis(
            short=short,
            level=level,
            value=round(level / SKILL_MAX_LEVEL * 100),
        )
        for short, level in zip(RADAR_AXES, levels, strict=True)
    ]


def skill_score(axes: list[SkillAxis]) -> int:
    """Overall 0-5 skill score: the rounded mean of its three axis levels."""
    if not axes:
        return 0
    return round(sum(axis.level for axis in axes) / len(axes))


def skill_matches(name: str, aliases: tuple[str, ...]) -> bool:
    """Tell whether a skill name matches one of a priority skill's aliases."""
    normalized = " ".join(name.strip().lower().split())
    for alias in aliases:
        if alias == "sql" and "nosql" in normalized:
            continue
        if alias in normalized:
            return True
    return False


def gap_status(months: int) -> Status:
    """Traffic-light colour for one employment gap by its length."""
    if months > GAP_CRITICAL_MONTHS:
        return "negative"
    if months >= GAP_ATTENTION_MONTHS:
        return "attention"
    return "neutral"


def tenure_status(months: int) -> Status:
    """Career-ring colour for one job: a year or more green, shorter yellow."""
    return "positive" if months >= JOB_FULL_YEAR_MONTHS else "attention"


def gaps_overall_status(gap_months: list[int]) -> Status:
    """Worst-case traffic-light colour across all employment gaps."""
    statuses = [gap_status(months) for months in gap_months]
    if "negative" in statuses:
        return "negative"
    if "attention" in statuses:
        return "attention"
    return "positive"


def gaps_label(gap_months: list[int]) -> str:
    """Short glance label summarising the candidate's employment gaps.

    The tile is already titled "Перерывы", so the value carries only the
    duration, never the word again.
    """
    if not gap_months:
        return "Без перерывов"
    if len(gap_months) == 1:
        return duration_label(gap_months[0])
    return f"{len(gap_months)}, всего {duration_label(sum(gap_months))}"


def radar_points(axes: list[SkillAxis]) -> str:
    """Project axis values onto an SVG polygon 'x,y x,y ...' string."""
    points: list[str] = []
    count = len(axes)
    for index, axis in enumerate(axes):
        angle = math.radians(-90 + index * (360 / count))
        radius = max(0, min(100, axis.value)) / 100 * RADAR_RADIUS
        x = RADAR_CENTER + radius * math.cos(angle)
        y = RADAR_CENTER + radius * math.sin(angle)
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)
