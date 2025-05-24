"""Configuration classes and constants for Gemini Music."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class PromptType(Enum):
    """Available prompt types."""
    ANALYZE = "analyze"
    EVAL = "eval"
    SUNO = "suno"


@dataclass
class AudioConfig:
    """Configuration for audio download and processing."""
    bitrate: int = 128
    format: str = 'mp3'
    socket_timeout: int = 60
    retries: int = 3
    fragment_retries: int = 3
    user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'


@dataclass
class GeminiConfig:
    """Configuration for Gemini AI processing."""
    model: str = "gemini-2.5-flash-preview-05-20"
    api_version: str = "v1beta"
    timeout: int = 180


class AudioFormats:
    """Supported audio file extensions."""
    EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'}
    
    MIME_TYPES = {
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'm4a': 'audio/mp4',
        'flac': 'audio/flac',
        'ogg': 'audio/ogg',
        'aac': 'audio/aac'
    }


class YouTubePatterns:
    """YouTube URL regex patterns."""
    PATTERNS = [
        r'(?:https?://)(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?://)(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
        r'(?:https?://)(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)',
        r'(?:https?://)(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]+)'
    ]


# Default configurations
DEFAULT_AUDIO_CONFIG = AudioConfig()
DEFAULT_GEMINI_CONFIG = GeminiConfig()