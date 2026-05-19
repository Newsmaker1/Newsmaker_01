from enum import Enum


class SubscriptionPlan(str, Enum):
    NEWS = "news"
    CITY = "city"
    DIASPORA = "diaspora"


class DestinationType(str, Enum):
    PRIVATE = "private"
    CHANNEL = "channel"
    GROUP = "group"
    FORUM_TOPIC = "forum_topic"


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"
    SKIPPED = "skipped"


class PostStatus(str, Enum):
    NEW = "new"
    PROCESSED = "processed"
    PUBLISHED = "published"
    FAILED = "failed"


class SupportStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    IN_PROGRESS = "in_progress"


class SourceType(str, Enum):
    RSS = "rss"
    CITY = "city"


class LogLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
