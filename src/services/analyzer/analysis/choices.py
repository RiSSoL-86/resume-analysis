from enum import StrEnum


class Status(StrEnum):
    """Traffic-light verdict shared across the report and dashboard."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    ATTENTION = "attention"
    NEGATIVE = "negative"
    UNKNOWN = "unknown"


class Severity(StrEnum):
    """How serious a risk or screening question is, worst first."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EvidenceLevel(StrEnum):
    """How strongly a skill is backed by the resume, weakest first."""

    NOT_FOUND = "not_found"
    CLAIMED_ONLY = "claimed_only"
    PROJECT_CONTEXT = "project_context"
    CONCRETE_APPLICATION = "concrete_application"
    COMPLEX_TASK = "complex_task"
    MEASURABLE_RESULT = "measurable_result"


class EstimatedLevel(StrEnum):
    """The candidate's estimated seniority ladder, lowest to highest."""

    INTERN = "intern"
    JUNIOR = "junior"
    JUNIOR_PLUS = "junior_plus"
    MIDDLE_MINUS = "middle_minus"
    MIDDLE = "middle"
    MIDDLE_PLUS = "middle_plus"
    SENIOR = "senior"
    LEAD = "lead"
    UNKNOWN = "unknown"


class EstimatedDepth(StrEnum):
    """Depth of ownership of a single skill, shallowest first."""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    UNKNOWN = "unknown"


class MainProfile(StrEnum):
    """Target-role key: the analyst family, a generic developer, or other."""

    SYSTEM_ANALYST = "system_analyst"
    BUSINESS_ANALYST = "business_analyst"
    PRODUCT_ANALYST = "product_analyst"
    DATA_ANALYST = "data_analyst"
    BI_ANALYST = "bi_analyst"
    DEVELOPER = "developer"
    OTHER = "other"


class RoleRelevance(StrEnum):
    """How relevant a past job is to the candidate's target role."""

    CORE = "core"
    ADJACENT = "adjacent"
    UNRELATED = "unrelated"


class Sector(StrEnum):
    """The employer's industry sector, classified by the model."""

    BANKING = "banking"
    FINTECH = "fintech"
    INSURANCE = "insurance"
    INVESTMENT = "investment"
    TELECOM = "telecom"
    RETAIL = "retail"
    ECOMMERCE = "ecommerce"
    IT_SERVICES = "it_services"
    MEDIA = "media"
    GAMEDEV = "gamedev"
    TRANSPORT = "transport"
    MANUFACTURING = "manufacturing"
    ENERGY = "energy"
    HEALTHCARE = "healthcare"
    GOVERNMENT = "government"
    EDUCATION = "education"
    OTHER = "other"
    UNKNOWN = "unknown"


class MetadataStatus(StrEnum):
    """Analysis lifecycle status, owned by the application, not the model."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class EducationKind(StrEnum):
    """Whether an education record is a full degree or a shorter course."""

    DEGREE = "degree"
    COURSE = "course"
