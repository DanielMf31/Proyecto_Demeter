class AppError(Exception):
    """Base exception for application errors."""
    pass

class ConfigurationError(AppError):
    """Configuration related errors."""
    pass

class HardwareError(AppError):
    """Hardware communication errors."""
    pass
