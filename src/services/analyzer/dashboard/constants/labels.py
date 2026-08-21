from typing import Final

from services.analyzer.analysis.choices import (
    EstimatedLevel,
    MainProfile,
    Sector,
)

LEVEL_LABELS: Final[dict[EstimatedLevel, str]] = {
    EstimatedLevel.INTERN: "Стажёр",
    EstimatedLevel.JUNIOR: "Junior",
    EstimatedLevel.JUNIOR_PLUS: "Junior+",
    EstimatedLevel.MIDDLE_MINUS: "Middle−",
    EstimatedLevel.MIDDLE: "Middle",
    EstimatedLevel.MIDDLE_PLUS: "Middle+",
    EstimatedLevel.SENIOR: "Senior",
    EstimatedLevel.LEAD: "Lead",
    EstimatedLevel.UNKNOWN: "Не определён",
}
PROFILE_LABELS: Final[dict[MainProfile, str]] = {
    MainProfile.SYSTEM_ANALYST: "Системный аналитик",
    MainProfile.BUSINESS_ANALYST: "Бизнес-аналитик",
    MainProfile.PRODUCT_ANALYST: "Продуктовый аналитик",
    MainProfile.DATA_ANALYST: "Аналитик данных",
    MainProfile.BI_ANALYST: "BI-аналитик",
    MainProfile.DEVELOPER: "Разработчик",
    MainProfile.OTHER: "Другой профиль",
}
# Short Russian labels for the sector hint printed under each job on the
# life-timeline; keyed by the model's Sector classification.
SECTOR_LABELS: Final[dict[Sector, str]] = {
    Sector.BANKING: "Банк",
    Sector.FINTECH: "Финтех",
    Sector.INSURANCE: "Страхование",
    Sector.INVESTMENT: "Инвестиции",
    Sector.TELECOM: "Телеком",
    Sector.RETAIL: "Ритейл",
    Sector.ECOMMERCE: "E-commerce",
    Sector.IT_SERVICES: "IT-услуги",
    Sector.MEDIA: "Медиа",
    Sector.GAMEDEV: "Геймдев",
    Sector.TRANSPORT: "Транспорт",
    Sector.MANUFACTURING: "Производство",
    Sector.ENERGY: "Энергетика",
    Sector.HEALTHCARE: "Медицина",
    Sector.GOVERNMENT: "Госсектор",
    Sector.EDUCATION: "Образование",
    Sector.OTHER: "Компания",
    Sector.UNKNOWN: "Компания",
}
# Currency codes rendered as symbols in the salary badge; unknown codes fall
# back to the raw code appended after the amount.
CURRENCY_SYMBOLS: Final[dict[str, str]] = {
    "RUB": "₽",
    "USD": "$",
    "EUR": "€",
}
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
