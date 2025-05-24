#!/usr/bin/env python3
"""
Gemini Music - A command-line interface for Gemini AI with audio file processing capabilities.

The tool supports multiple predefined prompt types that can be selected using the --prompt-type
flag, or users can provide custom prompts. Available predefined prompts include detailed music
analysis and song evaluation with scoring.

This is the refactored version using clean code principles.
"""

from .cli import main

if __name__ == "__main__":
    main()