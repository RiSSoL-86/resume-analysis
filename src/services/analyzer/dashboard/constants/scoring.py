from typing import Final

from services.analyzer.analysis.choices import (
    EstimatedDepth,
    EstimatedLevel,
    RoleRelevance,
    Severity,
    Status,
)

# Worst-first ordering for risks and questions: the Severity ladder reversed.
SEVERITY_ORDER: Final[tuple[Severity, ...]] = tuple(reversed(Severity))
SEVERITY_STATUS: Final[dict[Severity, Status]] = {
    Severity.CRITICAL: Status.NEGATIVE,
    Severity.HIGH: Status.NEGATIVE,
    Severity.MEDIUM: Status.ATTENTION,
    Severity.LOW: Status.NEUTRAL,
    Severity.INFO: Status.NEUTRAL,
}
# Overall candidate score (0-100): the single "worth attention?" number.
# A hybrid blend a recruiter reads at a glance — objective facts computed here
# (relevant tenure, stability, gaps) combined with the model's contextual
# judgment (role fit). Weights sum to 1.0; the blend is then discounted by
# career instability and employment gaps. Role-core skills and the model's
# role-fit lead, so a thin or ill-fitting profile visibly drags the rating.
OVERALL_SKILL_WEIGHT: Final[float] = 0.35
OVERALL_ROLE_FIT_WEIGHT: Final[float] = 0.30
OVERALL_LEVEL_WEIGHT: Final[float] = 0.20
OVERALL_EXPERIENCE_WEIGHT: Final[float] = 0.15
# Bank / fintech experience is a bonus for the target profile (added points),
# counted only from role-relevant jobs (see RELEVANCE_WEIGHTS).
OVERALL_DOMAIN_BONUS: Final[int] = 5
# Tenure that already counts as a full experience component (months): 5 years.
# Applied to role-relevant tenure only; unrelated work does not count here.
OVERALL_EXPERIENCE_FULL_MONTHS: Final[int] = 60
# How much a past job counts toward relevant tenure and the domain bonus, by
# the model's relevance verdict: profile work in full, adjacent roles at half,
# unrelated work not at all (e.g. a lathe operator applying as an analyst).
RELEVANCE_WEIGHTS: Final[dict[RoleRelevance, float]] = {
    RoleRelevance.CORE: 1.0,
    RoleRelevance.ADJACENT: 0.5,
    RoleRelevance.UNRELATED: 0.0,
}
# Career-stability discount: a job-hopping history (many sub-year stints)
# multiplies the blended score down. The floor is the multiplier at zero
# stability (every job under a year); an all-stable history keeps the full
# score. Stability = share of tenure spent in year-plus jobs.
OVERALL_STABILITY_FLOOR: Final[float] = 0.60
# Employment-gap penalty (points subtracted): significant gaps deduct from the
# score, saturating — this many total gap-months reaches the maximum deduction.
OVERALL_GAP_PENALTY_FULL_MONTHS: Final[int] = 18
OVERALL_GAP_PENALTY_MAX: Final[int] = 15
# Traffic-light thresholds for the overall candidate score.
OVERALL_POSITIVE: Final[int] = 65
OVERALL_ATTENTION: Final[int] = 45
# Traffic-light cut-offs for the headline tiles a recruiter reads at a glance.
# Total experience: under 3 years is red, 3-5 yellow, 5+ green.
EXPERIENCE_STRONG_MONTHS: Final[int] = 60
EXPERIENCE_ATTENTION_MONTHS: Final[int] = 36
# Seniority: middle+ and up green, middle−/middle yellow, junior and below red.
LEVEL_STRONG_RANK: Final[EstimatedLevel] = EstimatedLevel.MIDDLE_PLUS
LEVEL_ATTENTION_RANK: Final[EstimatedLevel] = EstimatedLevel.MIDDLE_MINUS
# Seniority ladder, lowest to highest, for the level component of the score.
LEVEL_RANKS: Final[tuple[EstimatedLevel, ...]] = tuple(
    level for level in EstimatedLevel if level is not EstimatedLevel.UNKNOWN
)
# Absolute 1-5 scoring — the same bar for every candidate, not relative to one
# resume. Calibrated for the Alfa-Bank IT hiring pool (3-6 and 6+ years):
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
# Skill colour by its 0-5 score (mean of mentions, tenure and depth): 4+ is
# a proven skill (green), 2-3 is partial (yellow), 0-1 is thin (red).
SKILL_SCORE_STRONG: Final[int] = 4
SKILL_SCORE_ATTENTION: Final[int] = 2
# Depth of ownership maps straight onto the 1-5 scale (0 = not established).
DEPTH_LEVELS: Final[dict[EstimatedDepth, int]] = {
    EstimatedDepth.UNKNOWN: 0,
    EstimatedDepth.BASIC: 2,
    EstimatedDepth.INTERMEDIATE: 3,
    EstimatedDepth.ADVANCED: 4,
    EstimatedDepth.EXPERT: 5,
}
