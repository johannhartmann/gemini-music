"""Service classes for Gemini Music processing."""

import os
import tempfile
import re
from pathlib import Path
from typing import List, Tuple, Optional
import yt_dlp
from google import genai
from google.genai.types import HttpOptions

from .config import (
    AudioConfig, GeminiConfig, AudioFormats, YouTubePatterns,
    DEFAULT_AUDIO_CONFIG, DEFAULT_GEMINI_CONFIG
)
from .prompts import PromptManager
from .exceptions import AudioDownloadError, AudioProcessingError, InvalidInputError


class AudioDownloader:
    """Service for downloading audio from YouTube URLs."""
    
    def __init__(self, config: AudioConfig = DEFAULT_AUDIO_CONFIG):
        self.config = config
    
    def is_youtube_url(self, url: str) -> bool:
        """Check if a string is a YouTube URL."""
        return any(re.match(pattern, url) for pattern in YouTubePatterns.PATTERNS)
    
    def download_from_youtube(self, url: str) -> Path:
        """Download audio from YouTube URL to a temporary file using yt-dlp."""
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Configure yt-dlp options for audio-only download
            ydl_opts = {
                'format': f'bestaudio[abr<={self.config.bitrate}]/best[abr<={self.config.bitrate}]',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.config.format,
                    'preferredquality': str(self.config.bitrate),
                }],
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': self.config.socket_timeout,
                'retries': self.config.retries,
                'fragment_retries': self.config.fragment_retries,
                'http_headers': {
                    'User-Agent': self.config.user_agent
                }
            }
            
            # Download the audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # yt-dlp might change the extension, so find the actual file
                temp_path = Path(temp_dir)
                downloaded_files = list(temp_path.glob('*'))
                
                if not downloaded_files:
                    raise AudioDownloadError("No file was downloaded")
                    
                return downloaded_files[0]
            
        except AudioDownloadError:
            raise
        except Exception as e:
            raise AudioDownloadError(f"Failed to download YouTube audio: {str(e)}")


class AudioProcessor:
    """Service for processing audio files with Gemini AI."""
    
    def __init__(self, client, config: GeminiConfig = DEFAULT_GEMINI_CONFIG):
        self.client = client
        self.config = config
        self.prompt_manager = PromptManager()
    
    def process_file(self, file_path: Path, prompt: str) -> str:
        """Process a single audio file with the Gemini API."""
        try:
            # Load audio file content
            with open(file_path, 'rb') as f:
                audio_data = f.read()
                
            # Determine the MIME type based on file extension
            file_ext = file_path.suffix.lower()[1:]  # Remove the leading dot
            mime_type = AudioFormats.MIME_TYPES.get(file_ext, f"audio/{file_ext}")
            
            # Create content parts using the proper Part.from_bytes method
            from google.genai import types
            audio_part = types.Part.from_bytes(
                data=audio_data,
                mime_type=mime_type
            )
            
            # Generate content with the audio file
            print("Sending audio to Gemini AI for analysis...")
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=[prompt, audio_part]
            )
            
            return response.text
        except Exception as e:
            raise AudioProcessingError(f"Error processing file {file_path.name}: {str(e)}")
    
    def process_file_two_step(self, file_path: Path, step1_prompt: str, step2_prompt: str) -> Tuple[str, str]:
        """Process a single audio file with a two-step prompt approach."""
        try:
            # Step 1: Process audio file with first prompt
            step1_response = self.process_file(file_path, step1_prompt)
            
            # Step 2: Process the first response with second prompt (text-only)
            step2_response = self.client.models.generate_content(
                model=self.config.model,
                contents=[step2_prompt + "\n\nAnalysis to convert:\n" + step1_response]
            )
            
            return step1_response, step2_response.text
        except AudioProcessingError:
            raise
        except Exception as e:
            raise AudioProcessingError(f"Error processing file {file_path.name}: {str(e)}")
    
    def process_file_three_step(self, file_path: Path, step1_prompt: str, step2_prompt: str, step3_prompt: str) -> Tuple[str, str, str]:
        """Process a single audio file with a three-step prompt approach."""
        try:
            # Step 1: Process audio file with first prompt
            step1_response = self.process_file(file_path, step1_prompt)
            
            # Step 2: Process the first response with second prompt (text-only)
            step2_response = self.client.models.generate_content(
                model=self.config.model,
                contents=[step2_prompt + "\n\nAnalysis to convert:\n" + step1_response]
            )
            
            # Step 3: Process the first response with third prompt (text-only)
            step3_response = self.client.models.generate_content(
                model=self.config.model,
                contents=[step3_prompt + "\n\nAnalysis to convert:\n" + step1_response]
            )
            
            return step1_response, step2_response.text, step3_response.text
        except AudioProcessingError:
            raise
        except Exception as e:
            raise AudioProcessingError(f"Error processing file {file_path.name}: {str(e)}")
    
    def process_directory(self, directory: Path, prompt: str) -> List[Tuple[str, str]]:
        """Process all audio files in a directory."""
        results = []
        
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in AudioFormats.EXTENSIONS:
                try:
                    response = self.process_file(file_path, prompt)
                    results.append((file_path.name, response))
                except AudioProcessingError as e:
                    # Log error but continue with other files
                    results.append((file_path.name, f"Error: {str(e)}"))
        
        return results
    
    def process_directory_two_step(self, directory: Path, step1_prompt: str, step2_prompt: str) -> List[Tuple[str, Tuple[str, str]]]:
        """Process all audio files in a directory using two-step prompts."""
        results = []
        
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in AudioFormats.EXTENSIONS:
                try:
                    step1_response, step2_response = self.process_file_two_step(file_path, step1_prompt, step2_prompt)
                    results.append((file_path.name, (step1_response, step2_response)))
                except AudioProcessingError as e:
                    # Log error but continue with other files
                    error_msg = f"Error: {str(e)}"
                    results.append((file_path.name, (error_msg, error_msg)))
        
        return results
    
    def process_directory_three_step(self, directory: Path, step1_prompt: str, step2_prompt: str, step3_prompt: str) -> List[Tuple[str, Tuple[str, str, str]]]:
        """Process all audio files in a directory using three-step prompts."""
        results = []
        
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in AudioFormats.EXTENSIONS:
                try:
                    step1_response, step2_response, step3_response = self.process_file_three_step(file_path, step1_prompt, step2_prompt, step3_prompt)
                    results.append((file_path.name, (step1_response, step2_response, step3_response)))
                except AudioProcessingError as e:
                    # Log error but continue with other files
                    error_msg = f"Error: {str(e)}"
                    results.append((file_path.name, (error_msg, error_msg, error_msg)))
        
        return results


class InputValidator:
    """Service for validating and categorizing input types."""
    
    def __init__(self, downloader: AudioDownloader):
        self.downloader = downloader
    
    def detect_input_type(self, input_path: str) -> str:
        """Detect whether input is a YouTube URL, file, or directory."""
        if self.downloader.is_youtube_url(input_path):
            return "youtube"
        
        path = Path(input_path)
        if not path.exists():
            raise InvalidInputError(f"Path '{input_path}' does not exist")
        
        if path.is_file() and path.suffix.lower() in AudioFormats.EXTENSIONS:
            return "file"
        elif path.is_dir():
            return "directory"
        else:
            raise InvalidInputError(f"'{input_path}' is not a valid audio file, directory, or YouTube URL")


def create_gemini_client(api_key: str, config: GeminiConfig = DEFAULT_GEMINI_CONFIG):
    """Create and configure a Gemini client."""
    return genai.Client(
        api_key=api_key,
        http_options=HttpOptions(api_version=config.api_version)
    )