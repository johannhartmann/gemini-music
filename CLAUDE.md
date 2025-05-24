# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gemini Music is a command-line tool for processing audio files with Google's Gemini AI models. It sends audio files to the Gemini API along with a user-specified prompt and returns the AI's response.

## Environment Setup

```bash
# Install dependencies
pip install -e .

# Set Google API key in environment
export GOOGLE_API_KEY="your-api-key-here"
```

## Commands

### Run the CLI

```bash
# Process all audio files in a directory
gemini-music "Your prompt here" /path/to/audio/files

# Example with a specific prompt
gemini-music "Transcribe and summarize this audio" ./files

# Use predefined prompts
gemini-music --prompt-type analyze /path/to/audio/files
gemini-music --prompt-type eval /path/to/audio/files

# List available predefined prompts
gemini-music --list-prompts
```

## Code Architecture

The project has a dual-module structure with identical functionality:
- `gemini_cli.py`: The main module containing all application logic
- `gemini_cli/`: Package structure with the same code in `core.py` and exposed via `__init__.py`

### Key Functions
- `process_audio_file()`: Processes a single audio file
- `process_directory()`: Processes all audio files in a directory  
- `get_predefined_prompts()`: Returns dictionary of built-in prompts ("analyze" and "eval")
- `main()`: Entry point handling CLI arguments and setup

The application uses the Google GenAI Python SDK to interact with Gemini models, specifically targeting the `gemini-2.5-flash-preview-05-20` model for multimodal processing of audio files.

## Audio Processing

The CLI supports common audio formats including `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, and `.aac`. The MIME type is automatically determined from the file extension.

## Predefined Prompts

The tool includes two sophisticated predefined prompts:
- `analyze`: Comprehensive 10-section musical analysis covering genre, tempo, harmony, melody, instrumentation, dynamics, form, production, cultural context, and performance
- `eval`: Pop song evaluation system that scores 8 criteria and outputs structured JSON results