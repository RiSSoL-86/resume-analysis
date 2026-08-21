from typing import Final

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
# Resume-freshness colour by age of the last update (months): under a month is
# fresh (green), 1-3 months is ageing (yellow), older reads as stale (red).
RESUME_FRESH_MONTHS: Final[int] = 1
RESUME_STALE_MONTHS: Final[int] = 4
