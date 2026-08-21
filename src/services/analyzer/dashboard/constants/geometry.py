from typing import Final

# Hair-thin separation between stacked cards — just enough to avoid overlap.
CARD_GAP: Final = 2.0
# Recent, uncompressed zone: the last 10 years at a fixed step.
LINEAR_MONTHS: Final = 120
# The shortest span we design the scale around (~half a year). A minimum job or
# break card is icon-sized — the logo tile plus its two lines — and the recent
# scale is built FROM that floor: a 6-month span fills exactly one min-height
# card, so it sits on its true dates instead of overshooting them. The step is
# ~25% tighter than before, now that cards carry course-sized text.
MIN_SPAN_MONTHS: Final = 6
YEAR_STEP: Final = 62.0
MONTH_STEP: Final = YEAR_STEP / 12.0
# Compression past the linear zone: saturating curve
# ``step*relax*t/(t+relax)``, slope-continuous at the seam. Larger = gentler.
COMPRESS_RELAX: Final = 55.0
# Min gap (px) between year ticks before intermediate labels are dropped. Set
# wide enough that the compressed (older) zone shows only sparse years, while
# recent years — a full step apart — all survive. The start-of-study year is
# the oldest tick and is always kept (see ``_timeline_years``).
YEAR_LABEL_GAP: Final = 26.0
# Floor so a very short career still draws a timeline with some body.
AXIS_MIN_HEIGHT: Final = 360.0
# Per-kind card-height floors that keep the shortest stints legible. Jobs and
# breaks share a 6-month floor (see above): a 3-month break renders the same
# height as a 6-month one, so the shortest gaps stay readable and uniform.
MIN_HEIGHTS: Final = {
    "job": MONTH_STEP * MIN_SPAN_MONTHS,
    "gap": MONTH_STEP * MIN_SPAN_MONTHS,
    "education": 38.0,
    "course": 32.0,
}
