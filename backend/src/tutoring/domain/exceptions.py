"""Domain exceptions representing business rule and invariant violations."""


class DomainError(Exception):
    """Base exception for all domain-level errors."""


class ValidationError(DomainError):
    """Raised when an entity or value object violates a structural invariant."""


class InvalidAttemptError(DomainError):
    """Raised when an exercise attempt is semantically inconsistent."""


class EntityNotFoundError(DomainError):
    """Raised when a referenced domain entity does not exist."""


class DuplicateEntityError(DomainError):
    """Raised when attempting to register a duplicate entity or value."""
