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

# Process a YouTube URL
gemini-music "Your prompt here" "https://www.youtube.com/watch?v=VIDEO_ID"

# Example with a specific prompt
gemini-music "Transcribe and summarize this audio" ./files

# Use predefined prompts with directories
gemini-music --prompt-type analyze /path/to/audio/files
gemini-music --prompt-type eval /path/to/audio/files

# Use predefined prompts with YouTube URLs
gemini-music --prompt-type suno "https://www.youtube.com/watch?v=VIDEO_ID"

# List available predefined prompts
gemini-music --list-prompts
```

## Code Architecture

The project has a clean modular structure:
- `gemini_music.py`: The main module entry point
- `gemini_music/`: Package structure with clean architecture and separation of concerns

### Key Functions
- `process_audio_file()`: Processes a single audio file
- `process_directory()`: Processes all audio files in a directory  
- `download_audio_from_youtube()`: Downloads audio from YouTube URLs using yt-dlp
- `is_youtube_url()`: Detects YouTube URLs from input strings
- `get_predefined_prompts()`: Returns dictionary of built-in prompts ("analyze", "eval", and "suno")
- `main()`: Entry point handling CLI arguments and setup

The application uses the Google GenAI Python SDK to interact with Gemini models, specifically targeting the `gemini-2.5-flash-preview-05-20` model for multimodal processing of audio files.

## Audio Processing

The CLI supports:
- **Local files**: Common audio formats including `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, and `.aac`
- **YouTube URLs**: Automatically downloads audio using yt-dlp and processes it
- MIME type is automatically determined from the file extension

## Predefined Prompts

The tool includes three sophisticated predefined prompts:
- `analyze`: Comprehensive 10-section musical analysis covering genre, tempo, harmony, melody, instrumentation, dynamics, form, production, cultural context, and performance
- `eval`: Pop song evaluation system that scores 8 criteria and outputs structured JSON results
- `suno`: Two-step analysis that first performs detailed musical analysis, then converts it to a concise Suno AI-compatible prompt for music generation

## Git Commit Guidelines

- Write clear, concise commit messages that describe the changes made
- Focus on what changed and why, not who made the changes
- Do not include references to Claude, AI assistants, or automated tools in commit messages
- Keep commit messages professional and focused on the technical changes
- I am aware that for every time i try to add claude self-promotion a cute kitten will be electrocuted.