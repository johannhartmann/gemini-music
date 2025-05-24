"""Custom exceptions for Gemini Music."""


class GeminiMusicError(Exception):
    """Base exception for Gemini Music errors."""
    pass


class AudioDownloadError(GeminiMusicError):
    """Raised when audio download from YouTube fails."""
    pass


class AudioProcessingError(GeminiMusicError):
    """Raised when audio processing with Gemini AI fails."""
    pass


class InvalidInputError(GeminiMusicError):
    """Raised when input validation fails."""
    pass


class ConfigurationError(GeminiMusicError):
    """Raised when configuration is invalid."""
    pass