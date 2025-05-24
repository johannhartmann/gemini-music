"""Clean CLI interface for Gemini Music."""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from .config import PromptType, DEFAULT_AUDIO_CONFIG, DEFAULT_GEMINI_CONFIG
from .services import AudioDownloader, AudioProcessor, InputValidator, create_gemini_client
from .prompts import PromptManager
from .exceptions import AudioDownloadError, AudioProcessingError, InvalidInputError, ConfigurationError


class GeminiMusicCLI:
    """Main CLI application class."""
    
    def __init__(self):
        self.downloader = AudioDownloader(DEFAULT_AUDIO_CONFIG)
        self.validator = InputValidator(self.downloader)
        self.prompt_manager = PromptManager()
        self.processor: Optional[AudioProcessor] = None
    
    def create_argument_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description="Process audio files with Gemini AI for detailed musical analysis - Gemini Music"
        )
        
        # Information/utility arguments
        info_group = parser.add_argument_group("Information Options")
        info_group.add_argument(
            "--list-prompts", "-lp",
            action="store_true",
            help="List all available predefined prompts and exit"
        )
        
        # Processing arguments
        proc_group = parser.add_argument_group("Processing Options")
        proc_group.add_argument(
            "input", 
            nargs="?",
            help="Audio file, directory containing audio files, or YouTube URL to process"
        )
        proc_group.add_argument(
            "prompt", 
            nargs="?",
            default=None,
            help="Custom prompt to send to Gemini with each audio file (optional, uses default music analysis prompt if not provided)"
        )
        proc_group.add_argument(
            "--prompt-type", "-p",
            choices=[pt.value for pt in PromptType],
            help="Select from predefined prompt types"
        )
        
        return parser
    
    def handle_list_prompts(self):
        """Handle the --list-prompts command."""
        print("Available Predefined Prompts:")
        print("-" * 50)
        for prompt_type in PromptType:
            print(f"- {prompt_type.value}")
        print("-" * 50)
        print("\\nUse --prompt-type [NAME] to select a predefined prompt")
        sys.exit(0)
    
    def setup_gemini_client(self):
        """Initialize the Gemini client."""
        # Load environment variables from .env file
        load_dotenv()
        
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ConfigurationError("GOOGLE_API_KEY environment variable not set")
        
        try:
            client = create_gemini_client(api_key, DEFAULT_GEMINI_CONFIG)
            self.processor = AudioProcessor(client, DEFAULT_GEMINI_CONFIG)
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Gemini client: {str(e)}")
    
    def determine_prompt(self, args) -> tuple:
        """Determine which prompt to use based on arguments."""
        if args.prompt_type:
            prompt_type = PromptType(args.prompt_type)
            prompt_data = self.prompt_manager.get_prompt(prompt_type)
            is_multi_step = prompt_type == PromptType.SUNO
            steps = len(prompt_data) if isinstance(prompt_data, dict) else 1
            step_desc = f" ({steps}-step analysis)" if is_multi_step else ""
            print(f"Using predefined prompt: {args.prompt_type}{step_desc}")
            return prompt_data, is_multi_step, steps
        elif args.prompt is None:
            prompt_data = self.prompt_manager.get_default_prompt()
            print("Using default detailed music analysis prompt")
            return prompt_data, False, 1
        else:
            return args.prompt, False, 1
    
    def process_youtube_url(self, url: str, prompt_data, is_multi_step: bool, steps: int):
        """Process a YouTube URL."""
        print(f"Downloading audio from YouTube URL: {url}")
        temp_audio_file = self.downloader.download_from_youtube(url)
        print(f"Downloaded to: {temp_audio_file}")
        
        try:
            if is_multi_step and steps == 3:
                step1_response, step2_response, step3_response = self.processor.process_file_three_step(
                    temp_audio_file, prompt_data["step1"], prompt_data["step2"], prompt_data["step3"]
                )
                self._print_three_step_results(temp_audio_file.name, step1_response, step2_response, step3_response)
            elif is_multi_step and steps == 2:
                step1_response, step2_response = self.processor.process_file_two_step(
                    temp_audio_file, prompt_data["step1"], prompt_data["step2"]
                )
                self._print_two_step_results(temp_audio_file.name, step1_response, step2_response)
            else:
                response = self.processor.process_file(temp_audio_file, prompt_data)
                self._print_single_result(temp_audio_file.name, response)
        finally:
            # Clean up temporary file
            if temp_audio_file.exists():
                temp_audio_file.unlink()
            if temp_audio_file.parent.exists():
                temp_audio_file.parent.rmdir()
    
    def process_single_file(self, file_path: Path, prompt_data, is_multi_step: bool, steps: int):
        """Process a single audio file."""
        if is_multi_step and steps == 3:
            step1_response, step2_response, step3_response = self.processor.process_file_three_step(
                file_path, prompt_data["step1"], prompt_data["step2"], prompt_data["step3"]
            )
            self._print_three_step_results(file_path.name, step1_response, step2_response, step3_response)
        elif is_multi_step and steps == 2:
            step1_response, step2_response = self.processor.process_file_two_step(
                file_path, prompt_data["step1"], prompt_data["step2"]
            )
            self._print_two_step_results(file_path.name, step1_response, step2_response)
        else:
            response = self.processor.process_file(file_path, prompt_data)
            self._print_single_result(file_path.name, response)
    
    def process_directory(self, directory_path: Path, prompt_data, is_multi_step: bool, steps: int):
        """Process all audio files in a directory."""
        if is_multi_step and steps == 3:
            results = self.processor.process_directory_three_step(
                directory_path, prompt_data["step1"], prompt_data["step2"], prompt_data["step3"]
            )
            
            if not results:
                print("No audio files found in the specified directory.")
                return
            
            for filename, (step1_response, step2_response, step3_response) in results:
                self._print_three_step_results(filename, step1_response, step2_response, step3_response)
        elif is_multi_step and steps == 2:
            results = self.processor.process_directory_two_step(
                directory_path, prompt_data["step1"], prompt_data["step2"]
            )
            
            if not results:
                print("No audio files found in the specified directory.")
                return
            
            for filename, (step1_response, step2_response) in results:
                self._print_two_step_results(filename, step1_response, step2_response)
        else:
            results = self.processor.process_directory(directory_path, prompt_data)
            
            if not results:
                print("No audio files found in the specified directory.")
                return
            
            for filename, response in results:
                self._print_single_result(filename, response)
    
    def _print_single_result(self, filename: str, response: str):
        """Print results for single-step processing."""
        print(f"\\n--- {filename} ---")
        print(response)
        print("-" * (len(filename) + 8))
    
    def _print_two_step_results(self, filename: str, step1_response: str, step2_response: str):
        """Print results for two-step processing."""
        print(f"\\n--- {filename} ---")
        print("=== DETAILED ANALYSIS ===")
        print(step1_response)
        print("\\n=== SUNO STYLE PROMPT ===")
        print(step2_response)
        print("-" * (len(filename) + 8))
    
    def _print_three_step_results(self, filename: str, step1_response: str, step2_response: str, step3_response: str):
        """Print results for three-step processing."""
        print(f"\\n--- {filename} ---")
        print("=== DETAILED ANALYSIS ===")
        print(step1_response)
        print("\\n=== SUNO STYLE PROMPT ===")
        print(step2_response)
        print("\\n=== SUNO LYRICS PROMPT ===")
        print(step3_response)
        print("-" * (len(filename) + 8))
    
    def run(self, args=None):
        """Main entry point for the CLI application."""
        parser = self.create_argument_parser()
        args = parser.parse_args(args)
        
        # Handle informational commands first
        if args.list_prompts:
            self.handle_list_prompts()
        
        # Require input for processing
        if not args.input:
            parser.print_help()
            print("\\nError: Directory or YouTube URL is required for processing audio files", file=sys.stderr)
            sys.exit(1)
        
        try:
            # Setup Gemini client
            self.setup_gemini_client()
            
            # Determine prompt configuration
            prompt_data, is_multi_step, steps = self.determine_prompt(args)
            
            # Detect input type and process accordingly
            input_type = self.validator.detect_input_type(args.input)
            
            if input_type == "youtube":
                self.process_youtube_url(args.input, prompt_data, is_multi_step, steps)
            elif input_type == "file":
                self.process_single_file(Path(args.input), prompt_data, is_multi_step, steps)
            elif input_type == "directory":
                self.process_directory(Path(args.input), prompt_data, is_multi_step, steps)
                
        except ConfigurationError as e:
            print(f"Configuration Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
        except InvalidInputError as e:
            print(f"Input Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
        except AudioDownloadError as e:
            print(f"Download Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
        except AudioProcessingError as e:
            print(f"Processing Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected Error: {str(e)}", file=sys.stderr)
            sys.exit(1)


def main():
    """Entry point function."""
    cli = GeminiMusicCLI()
    cli.run()