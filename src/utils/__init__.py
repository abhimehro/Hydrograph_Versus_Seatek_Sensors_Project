import typing
import logging

class HydrographProcessingError(Exception):
    """Base exception for Hydrograph processing errors."""

    def __init__(self, message: str, context: typing.Optional[typing.Dict[str, typing.Any]] = None):
        super().__init__(message)
        self.context = context or {}

    def __str__(self):
        base_message = super().__str__()
        if self.context:
            return f"{base_message} | Context: {self.context}"
        return base_message

    def log_error(self, logger: typing.Optional[logging.Logger] = None):
        """Logs the error using the provided logger or the default logger."""
        if logger is None:
            logger = logging.getLogger(__name__)
        logger.error(self.__str__())

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Converts the exception details to a dictionary."""
        return {
            'message': str(self),
            'context': self.context
        }

    def sanitize_context(self):
        """Sanitizes the context to remove sensitive information."""
        # Implement specific logic to sanitize sensitive data
        sanitized_context = {k: v for k, v in self.context.items() if not self.is_sensitive(k)}
        self.context = sanitized_context

    @staticmethod
    def is_sensitive(key: str) -> bool:
        """Determines if a context key is sensitive."""
        # Define logic to identify sensitive keys
        sensitive_keys = {'password', 'secret', 'token'}
        return key.lower() in sensitive_keys