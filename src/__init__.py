from typing import Optional, Dict, Any

class HydrographProcessingError(Exception):
    """Base exception for Hydrograph processing errors."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.context = context or {}

    def __str__(self):
        base_message = super().__str__()
        if self.context:
            return f"{base_message} | Context: {self.context}"
        return base_message

    def log_error(self, logger):
        """Logs the error using the provided logger."""
        logger.error(self.__str__())

    def to_dict(self) -> Dict[str, Any]:
        """Converts the exception details to a dictionary."""
        return {
            'message': str(self),
            'context': self.context
        }