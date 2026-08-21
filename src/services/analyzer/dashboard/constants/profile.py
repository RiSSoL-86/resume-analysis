from typing import Final

from services.analyzer.analysis.choices import Sector

# Domain experience that is a bonus for the Alfa-Bank hiring pool. Role-level
# configuration only: the model classifies each employer's sector, and this set
# lists which sectors count as the bonus domain — never keyed to company names.
PRIORITY_DOMAIN_LABEL: Final[str] = "Банк / финтех"
PRIORITY_DOMAIN_SECTORS: Final[frozenset[Sector]] = frozenset(
    {Sector.BANKING, Sector.FINTECH, Sector.INSURANCE, Sector.INVESTMENT}
)
