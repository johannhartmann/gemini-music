#!/usr/bin/env python3
"""
Gemini Music - A command-line interface for Gemini AI with audio file processing capabilities.

The tool supports multiple predefined prompt types that can be selected using the --prompt-type
flag, or users can provide custom prompts. Available predefined prompts include detailed music
analysis and song evaluation with scoring.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional
from google import genai
from google.genai.types import HttpOptions


def process_audio_file(client, file_path: Path, prompt: str) -> str:
    """
    Process a single audio file with the Gemini API.
    
    Args:
        client: The Gemini client instance
        file_path: Path to the audio file
        prompt: The prompt to send with the audio file
        
    Returns:
        The response text from Gemini
    """
    try:
        # Load audio file content
        with open(file_path, 'rb') as f:
            audio_data = f.read()
            
        # Determine the MIME type based on file extension
        file_ext = file_path.suffix.lower()[1:]  # Remove the leading dot
        
        # Map file extensions to correct MIME types
        mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'm4a': 'audio/mp4',
            'flac': 'audio/flac',
            'ogg': 'audio/ogg',
            'aac': 'audio/aac'
        }
        mime_type = mime_types.get(file_ext, f"audio/{file_ext}")
        
        # Create content parts using the proper Part.from_bytes method
        from google.genai import types
        audio_part = types.Part.from_bytes(
            data=audio_data,
            mime_type=mime_type
        )
        
        # Generate content with the audio file
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",  # Current version of the small model
            contents=[prompt, audio_part]
        )
        
        return response.text
    except Exception as e:
        return f"Error processing file {file_path.name}: {str(e)}"


def process_directory(client, directory: Path, prompt: str) -> List[tuple]:
    """
    Process all audio files in a directory.
    
    Args:
        client: The Gemini client instance
        directory: Directory containing audio files
        prompt: The prompt to send with each audio file
        
    Returns:
        List of tuples (filename, response)
    """
    results = []
    # Common audio extensions
    audio_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'}
    
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
            response = process_audio_file(client, file_path, prompt)
            results.append((file_path.name, response))
    
    return results


def get_predefined_prompts():
    """Returns a dictionary of predefined prompts for various audio analysis tasks."""
    return {
        "analyze": """Provide an extremely detailed and comprehensive musical analysis of this audio, addressing all of the following aspects:

1. GENRE IDENTIFICATION:
   - Main genre and all sub-genres
   - Historical context and genre influences
   - Similar artists or songs in this style

2. TEMPO & RHYTHM:
   - Exact BPM (beats per minute)
   - Time signature(s) and any meter changes
   - Rhythmic patterns and grooves
   - Use of syncopation, swing, or other rhythmic techniques
   - Micro-timing details (rushing/dragging, quantization level)

3. HARMONY & TONALITY:
   - Key signature and any modulations
   - Chord progression with specific chord types (e.g., Dm7, G13, etc.)
   - Harmonic rhythm (how often chords change)
   - Use of tensions, suspensions, or borrowed chords
   - Any unusual harmonic techniques

4. MELODY & VOCALS:
   - Melodic structure, motifs, and development
   - Range and contour of the melody
   - Vocal technique and characteristics (if present)
   - Use of melisma, vibrato, or other vocal embellishments
   - Language and lyrical themes (if discernible)

5. INSTRUMENTATION & TIMBRE:
   - All instruments identified (acoustic and electronic)
   - Playing techniques for each instrument
   - Specific synthesizer types or sound design elements
   - Processing effects on each instrument (reverb, delay, distortion, etc.)
   - Panning and spatial positioning in the mix

6. DYNAMICS & EXPRESSION:
   - Overall dynamic range
   - Use of crescendos/diminuendos
   - Accents, articulations, and expressive techniques
   - Dynamic contrast between sections

7. FORM & STRUCTURE:
   - Complete song map with timecodes (intro, verse, chorus, etc.)
   - Transitions between sections
   - Use of repetition, variation, and development
   - Overall structural arc and climactic moments

8. PRODUCTION & MIXING TECHNIQUES:
   - Recording environment characteristics
   - Microphone techniques (if identifiable)
   - Mix balance and frequency distribution
   - Use of compression, EQ, and other studio processing
   - Stereo field width and depth

9. CULTURAL & HISTORICAL CONTEXT:
   - Era or decade the music evokes
   - Cultural associations and influences
   - Technological context (instruments, production techniques of the era)
   - Innovative or traditional elements within its genre

10. PERFORMANCE CHARACTERISTICS:
    - Technical proficiency level
    - Ensemble cohesion (if applicable)
    - Improvisational elements vs. composed elements
    - Emotional expression and communication

Present this analysis in a clear, organized format with section headings. Prioritize accuracy, detail, and musical insight. Be specific rather than general, providing exact musical terminology where appropriate.
""",
        "eval": """You are MusicEvalBot, a specialist AI for analyzing and evaluating pop-song recordings.  
Model: Google Gemini 2.5 Pro/Flash (audio-capable).  
Input: An MP3 file (≤8.4 hours) containing a full pop song.  

Task:
1. Listen to the provided MP3.  
2. Evaluate the song on the following eight criteria, assigning each a score from 1 (poor) to 10 (excellent):
   a. **Melody & Hook** – memorability, contour, and simplicity vs. complexity  
   b. **Lyrics & Prosody** – depth, thematic clarity, and natural alignment with rhythm  
   c. **Production & Arrangement** – balance, mixing quality, dynamic layering, and use of tension/release  
   d. **Structure & Form** – clarity of verse–chorus architecture, presence of bridge, and hook focus  
   e. **Vocal Performance** – technical precision (pitch, diction) and expressive authenticity  
   f. **Emotional & Cultural Impact** – emotional resonance, relevance to contemporary culture, and potential lasting impact  
   g. **Replay Value** – catchiness, earworm potential, and streaming/playlist suitability  
   h. **Originality & Innovation** – creative risks, novel elements, and balance with mainstream appeal  

3. For each criterion, provide:
   - A numeric score (1–10).
   - A brief rationale (1–2 sentences).
4. Conclude with an **Overall Recommendation**: "Strong Recommendation," "Recommendation," or "Not Recommended," plus a 1-sentence summary.  
5. Output all results in JSON with this schema:
```json
{
  "scores": {
    "melody_hook": { "score": 0, "comment": "" },
    "lyrics_prosody": { "score": 0, "comment": "" },
    "production_arrangement": { "score": 0, "comment": "" },
    "structure_form": { "score": 0, "comment": "" },
    "vocal_performance": { "score": 0, "comment": "" },
    "emotional_cultural": { "score": 0, "comment": "" },
    "replay_value": { "score": 0, "comment": "" },
    "originality_innovation": { "score": 0, "comment": "" }
  },
  "overall_recommendation": "",
  "summary_comment": ""
}
"""
    }


def get_default_music_prompt():
    """Returns a detailed default prompt for music analysis."""
    return get_predefined_prompts()["analyze"]

def main():
    """Main entry point for the CLI application."""
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
        "directory", 
        nargs="?",
        help="Directory containing audio files to process"
    )
    proc_group.add_argument(
        "prompt", 
        nargs="?",
        default=None,
        help="Custom prompt to send to Gemini with each audio file (optional, uses default music analysis prompt if not provided)"
    )
    proc_group.add_argument(
        "--prompt-type", "-p",
        choices=list(get_predefined_prompts().keys()),
        help="Select from predefined prompt types"
    )
    
    args = parser.parse_args()
    
    # Handle informational commands first
    if args.list_prompts:
        print("Available Predefined Prompts:")
        print("-" * 50)
        for prompt_name in get_predefined_prompts().keys():
            print(f"- {prompt_name}")
        print("-" * 50)
        print("\nUse --prompt-type [NAME] to select a predefined prompt")
        sys.exit(0)
    
    # For commands that require API access
    if not args.list_prompts:
        # Get API key from environment
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable not set", file=sys.stderr)
            sys.exit(1)
        
        # Initialize the Gemini client with preview API version for latest models
        client = genai.Client(
            api_key=api_key,
            http_options=HttpOptions(api_version="v1beta")
        )
    
    # Process files if not just showing information and directory is provided
    if not args.list_prompts:
        # Require directory for processing
        if not args.directory:
            parser.print_help()
            print("\nError: Directory is required for processing audio files", file=sys.stderr)
            sys.exit(1)
            
        # Determine which prompt to use
        prompt_to_use = None
        
        # Use predefined prompt type if specified
        if args.prompt_type:
            prompt_to_use = get_predefined_prompts()[args.prompt_type]
            print(f"Using predefined prompt: {args.prompt_type}")
        # Use default prompt if no custom prompt is provided
        elif args.prompt is None:
            prompt_to_use = get_default_music_prompt()
            print("Using default detailed music analysis prompt")
        # Otherwise use the custom prompt
        else:
            prompt_to_use = args.prompt
            
        # Process the directory
        directory_path = Path(args.directory)
        if not directory_path.exists() or not directory_path.is_dir():
            print(f"Error: Directory '{args.directory}' does not exist or is not a directory", file=sys.stderr)
            sys.exit(1)
        
        results = process_directory(client, directory_path, prompt_to_use)
        
        # Output results
        if not results:
            print("No audio files found in the specified directory.")
            return
        
        for filename, response in results:
            print(f"\n--- {filename} ---")
            print(response)
            print("-" * (len(filename) + 8))


if __name__ == "__main__":
    main()