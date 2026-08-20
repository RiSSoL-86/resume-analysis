from typing import Final

LEVEL_LABELS: Final[dict[str, str]] = {
    "intern": "Стажёр",
    "junior": "Junior",
    "junior_plus": "Junior+",
    "middle_minus": "Middle−",
    "middle": "Middle",
    "middle_plus": "Middle+",
    "senior": "Senior",
    "lead": "Lead",
    "unknown": "Не определён",
}
PROFILE_LABELS: Final[dict[str, str]] = {
    "system_analyst": "Системный аналитик",
    "business_analyst": "Бизнес-аналитик",
    "product_analyst": "Продуктовый аналитик",
    "data_analyst": "Аналитик данных",
    "bi_analyst": "BI-аналитик",
}
SEVERITY_ORDER: Final[tuple[str, ...]] = (
    "critical",
    "high",
    "medium",
    "low",
    "info",
)
SEVERITY_STATUS: Final[dict[str, str]] = {
    "critical": "negative",
    "high": "negative",
    "medium": "attention",
    "low": "neutral",
    "info": "neutral",
}
# Overall candidate score (0-100): the single "worth attention?" number.
# A weighted blend a recruiter reads at a glance; weights sum to 1.0 and the
# must-have skills dominate because they define a system analyst — a missing
# must-have (score 0) visibly drags the rating down.
OVERALL_SKILL_WEIGHT: Final[float] = 0.60
OVERALL_LEVEL_WEIGHT: Final[float] = 0.25
OVERALL_EXPERIENCE_WEIGHT: Final[float] = 0.15
# Bank / fintech experience is a bonus for the target profile (added points).
OVERALL_DOMAIN_BONUS: Final[int] = 5
# Tenure that already counts as a full experience component (months): 5 years.
OVERALL_EXPERIENCE_FULL_MONTHS: Final[int] = 60
# Traffic-light thresholds for the overall candidate score.
OVERALL_POSITIVE: Final[int] = 65
OVERALL_ATTENTION: Final[int] = 45
# Traffic-light cut-offs for the headline tiles a recruiter reads at a glance.
# Total experience: under 3 years is red, 3-5 yellow, 5+ green.
EXPERIENCE_STRONG_MONTHS: Final[int] = 60
EXPERIENCE_ATTENTION_MONTHS: Final[int] = 36
# Seniority: middle+ and up green, middle−/middle yellow, junior and below red.
LEVEL_STRONG_RANK: Final[str] = "middle_plus"
LEVEL_ATTENTION_RANK: Final[str] = "middle_minus"
# Seniority ladder, lowest to highest, for the level component of the score.
LEVEL_RANKS: Final[tuple[str, ...]] = (
    "intern",
    "junior",
    "junior_plus",
    "middle_minus",
    "middle",
    "middle_plus",
    "senior",
    "lead",
)
# Skill radar geometry (three axes, drawn on a 100x100 SVG canvas).
# Each axis carries a short label shown at the SVG vertex.
RADAR_AXES: Final[tuple[str, ...]] = ("Упом.", "Стаж", "Глуб.")
RADAR_CENTER: Final[float] = 50.0
RADAR_RADIUS: Final[float] = 44.0
# Absolute 1-5 scoring — the same bar for every candidate, not relative to one
# resume. Calibrated for the target pool (system analysts, 3-6 and 6+ years):
# 3-5 years of a skill reads as level 4 and 5+ years as level 5.
SKILL_MAX_LEVEL: Final[int] = 5
# (lower_bound_inclusive, level) pairs, highest first. Months a skill was used.
TENURE_LEVEL_BANDS: Final[tuple[tuple[int, int], ...]] = (
    (60, 5),
    (36, 4),
    (18, 3),
    (6, 2),
    (1, 1),
)
# (lower_bound_inclusive, level) pairs, highest first. Mentions across resume.
MENTION_LEVEL_BANDS: Final[tuple[tuple[int, int], ...]] = (
    (7, 5),
    (5, 4),
    (3, 3),
    (2, 2),
    (1, 1),
)
# Skill radar colour, kept consistent with the drawn area so a bigger radar
# always reads greener. The score is the mean of the three axes (0-5): 4+ is
# a proven skill (green), 2-3 is partial (yellow), 0-1 is thin (red).
SKILL_SCORE_STRONG: Final[int] = 4
SKILL_SCORE_ATTENTION: Final[int] = 2
# Depth of ownership maps straight onto the 1-5 scale (0 = not established).
DEPTH_LEVELS: Final[dict[str, int]] = {
    "unknown": 0,
    "basic": 2,
    "intermediate": 3,
    "advanced": 4,
    "expert": 5,
}
# Domain experience that is a bonus for the system-analyst profile. Role-level
# configuration only: the model classifies each employer's sector, and this set
# lists which sectors count as the bonus domain — never keyed to company names.
PRIORITY_DOMAIN_LABEL: Final[str] = "Банк / финтех"
PRIORITY_DOMAIN_SECTORS: Final[frozenset[str]] = frozenset(
    {"banking", "fintech", "insurance", "investment"}
)
# Must-have skills for the system-analyst profile. Each is always drawn as a
# cube (even when absent), so a recruiter sees the whole checklist at a glance.
# Role-level configuration only — never keyed to a specific candidate.
PRIORITY_SKILLS: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    ("REST API", ("rest api", "restful", "rest", "http api")),
    ("Apache Kafka", ("kafka",)),
    ("OpenAPI/Swagger", ("openapi", "swagger", "oas")),
    ("SQL", ("sql",)),
    (
        "Сбор и формализация требований",
        ("требован", "формализац", "requirements"),
    ),
)
# Employment-gap thresholds (months), aligned with career_signals.yaml:
# under 3 is a seamless/short transition (ignored), 3-12 is yellow, 12+ red.
GAP_ATTENTION_MONTHS: Final[int] = 3
GAP_CRITICAL_MONTHS: Final[int] = 12
# Career-ring colour by time worked at one place: a year or more reads as
# stable (green), anything shorter is worth checking (yellow); gaps are red.
JOB_FULL_YEAR_MONTHS: Final[int] = 12
# Resumes carry only a graduation year, not a study start. To give education a
# proportional width on the life-timeline we assume a typical higher-education
# span ending at that year; the segment start is an estimate, not a fact.
STUDY_DEFAULT_MONTHS: Final[int] = 48
# Courses / certifications carry only a year, not a length. Give them a short
# fixed footprint so they read as point events on the study track (they often
# happen mid-career and must stay visible next to a full degree).
COURSE_DEFAULT_MONTHS: Final[int] = 6
# Russian month abbreviations for the life-timeline date labels, indexed 0-11
# (январь = 0). Kept terse to fit inside the positioned timeline cards.
MONTH_ABBR: Final[tuple[str, ...]] = (
    "янв.",
    "февр.",
    "март",
    "апр.",
    "май",
    "июнь",
    "июль",
    "авг.",
    "сент.",
    "окт.",
    "нояб.",
    "дек.",
)
# Short Russian labels for the sector hint printed under each job on the
# life-timeline; keyed by the model's Sector classification.
SECTOR_LABELS: Final[dict[str, str]] = {
    "banking": "Банк",
    "fintech": "Финтех",
    "insurance": "Страхование",
    "investment": "Инвестиции",
    "telecom": "Телеком",
    "retail": "Ритейл",
    "ecommerce": "E-commerce",
    "it_services": "IT-услуги",
    "media": "Медиа",
    "gamedev": "Геймдев",
    "transport": "Транспорт",
    "manufacturing": "Производство",
    "energy": "Энергетика",
    "healthcare": "Медицина",
    "government": "Госсектор",
    "education": "Образование",
    "other": "Компания",
    "unknown": "Компания",
}
# Currency codes rendered as symbols in the salary badge; unknown codes fall
# back to the raw code appended after the amount.
CURRENCY_SYMBOLS: Final[dict[str, str]] = {
    "RUB": "₽",
    "USD": "$",
    "EUR": "€",
}
# Resume-freshness colour by age of the last update (months): under a month is
# fresh (green), 1-3 months is ageing (yellow), older reads as stale (red).
RESUME_FRESH_MONTHS: Final[int] = 1
RESUME_STALE_MONTHS: Final[int] = 4
