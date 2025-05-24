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
import tempfile
import re
from pathlib import Path
from typing import List, Optional
from google import genai
from google.genai.types import HttpOptions
import yt_dlp


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


def process_audio_file_two_step(client, file_path: Path, step1_prompt: str, step2_prompt: str) -> tuple:
    """
    Process a single audio file with a two-step prompt approach.
    
    Args:
        client: The Gemini client instance
        file_path: Path to the audio file
        step1_prompt: The first prompt to send with the audio file
        step2_prompt: The second prompt to process the first result
        
    Returns:
        Tuple of (step1_response, step2_response)
    """
    try:
        # Step 1: Process audio file with first prompt
        step1_response = process_audio_file(client, file_path, step1_prompt)
        
        # Step 2: Process the first response with second prompt (text-only)
        step2_response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=[step2_prompt + "\n\nAnalysis to convert:\n" + step1_response]
        )
        
        return step1_response, step2_response.text
    except Exception as e:
        error_msg = f"Error processing file {file_path.name}: {str(e)}"
        return error_msg, error_msg


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


def process_directory_two_step(client, directory: Path, step1_prompt: str, step2_prompt: str) -> List[tuple]:
    """
    Process all audio files in a directory using two-step prompts.
    
    Args:
        client: The Gemini client instance
        directory: Directory containing audio files
        step1_prompt: The first prompt to send with each audio file
        step2_prompt: The second prompt to process the first result
        
    Returns:
        List of tuples (filename, (step1_response, step2_response))
    """
    results = []
    # Common audio extensions
    audio_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'}
    
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
            step1_response, step2_response = process_audio_file_two_step(client, file_path, step1_prompt, step2_prompt)
            results.append((file_path.name, (step1_response, step2_response)))
    
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
""",
        "suno": {
            "step1": """You are an expert music analyst AI. Your task is to perform a comprehensive musical analysis of the provided MP3 file. Please break down its characteristics in detail, covering the following aspects. Be as descriptive and specific as possible for each category:

Overall Impression & Core Identity:

Briefly summarize the track's essential sound and feeling in one or two sentences.
Genre and Subgenre Classification:

Identify the primary genre(s).
List any secondary genre influences or specific subgenres.
Provide a brief justification for your genre classifications, citing specific musical elements.
Mood, Atmosphere, and Evocative Qualities:

Describe the dominant mood(s) (e.g., joyful, melancholic, energetic, introspective, aggressive, dreamy, nostalgic).
Detail the overall atmosphere or vibe (e.g., cinematic, intimate, futuristic, vintage, raw, polished).
Include any evocative imagery or feelings the music conjures (e.g., "sounds like a chase scene," "evokes a sense of wonder," "perfect for a rainy day").
Tempo and Rhythm:

Specify the tempo (estimated BPM).
Describe the rhythmic feel and complexity (e.g., driving beat, laid-back groove, syncopated, polyrhythmic, straightforward, complex drum patterns, prominent rhythmic motifs).
Identify the time signature if clearly discernible and noteworthy.
Key and Tonality:

Identify the primary musical key and mode (e.g., C Major, A Minor, G Dorian).
Describe the overall tonality (e.g., diatonic, chromatic, atonal, bluesy).
Harmony and Chord Structure:

Describe the harmonic complexity (e.g., simple, rich, dissonant, consonant, jazz voicings, power chords).
Mention any notable chord progressions or harmonic characteristics that define the track's sound.
Instrumentation and Timbre:

List all clearly identifiable instruments.
For each key instrument, describe its role (e.g., lead melody, rhythmic accompaniment, bassline, harmonic support, atmospheric texture) and its specific timbral qualities (e.g., "distorted and aggressive electric guitar," "warm and resonant acoustic piano," "bright and punchy synth lead," "deep and smooth sub-bass," "crisp and tight drum kit").
Describe the overall sonic texture (e.g., sparse, dense, layered, transparent, muddy).
Vocal Characteristics (if applicable):

Describe the vocal presence (e.g., lead vocals, backing vocals, spoken word, ad-libs, instrumental).
Identify the perceived vocal type/gender and range (e.g., female soprano, male baritone, choir).
Detail the vocal delivery style (e.g., powerful, delicate, soulful, rapped, whispered, clean, gritty, auto-tuned).
Mention the presence and style of any vocal harmonies.
If discernible, note the language of the lyrics.
Song Structure and Form:

Outline the main sections of the song (e.g., Intro, Verse, Chorus, Bridge, Solo, Outro).
Describe the overall arrangement and how sections transition.
Note any unique structural elements or deviations from common forms.
Dynamics and Energy Contour:

Describe the overall energy level (e.g., high-energy, mellow, builds gradually).
Detail the dynamic range and any significant shifts in loudness or intensity throughout the track (e.g., "quiet, reflective verses contrasting with loud, expansive choruses," "gradual crescendo into the final section," "sudden drops in intensity").
Production Style and Effects:

Describe the overall production quality and style (e.g., polished and modern, raw and vintage, lo-fi, minimalist, heavily layered).
Mention any prominent audio effects used that significantly contribute to the sound (e.g., heavy reverb, delay on vocals, specific synth effects, noticeable compression, filter sweeps).
Please provide this analysis in a clear, well-organized textual format. Your detailed insights will be used to understand the essence of this music.""",
            "step2": """You are an AI assistant, an expert musicologist and creative writer, tasked with translating a detailed textual musical profile of an audio file into a rich, evocative, and concise descriptive prompt. This output prompt is specifically designed for the Suno AI music generation model (e.g., version 4.5 or similar). Your primary objective is to generate a single, well-written paragraph of descriptive text, strictly adhering to a maximum length of 1000 characters. This paragraph must capture the musical essence of the analyzed track to effectively guide Suno in generating a new piece of music.

You will be provided with a detailed textual musical profile. This profile will describe various aspects of the music, such as:
* **Core Musical Attributes:** Tempo (BPM), Key & Mode, Time Signature, Overall Energy Level.
* **Genre and Style:** Primary and secondary genres, stylistic descriptors.
* **Mood and Atmosphere:** Dominant moods and atmospheric qualities.
* **Instrumentation and Timbre:** Predominant instruments with their roles, timbral characteristics, playing styles, and any notable effects.
* **Vocal Characteristics (if applicable):** Vocal presence, type/gender, delivery style, lyrical themes (if inferable), and harmonies.
* **Structure and Dynamics:** Overall song structure, key sections, dynamic profile, and rhythmic feel.
* **Production and Sonic Quality:** Production style, soundstage/mix, and unique sonic signatures.

Your transformation logic should be as follows, drawing from the provided textual profile:

1.  **Genre Synthesis:** From the described genres, identify the primary genre(s). If one genre is clearly dominant, feature it prominently. If multiple genres are highlighted as significant, attempt to describe a blend or fusion (e.g., 'a compelling fusion of synthwave and dark ambient elements,' or 'an indie rock track with strong folk influences'). Use descriptive language that reflects the typical characteristics of these genres as detailed in the input profile. If the profile indicates ambiguity or an eclectic mix, reflect that.

2.  **Mood Articulation:** Synthesize information from the described moods, key/mode, tempo, and energy level to articulate the dominant mood(s). For instance, if the profile states "slow tempo, minor key, melancholic mood," describe it as 'deeply introspective and melancholic.' Leverage Suno's ability to understand nuanced emotional descriptions by using evocative adjectives based on the input.

3.  **Instrumentation Description:** Based on the listed instruments and their characteristics, describe the core instrumentation. Use vivid adjectives and specify instrument roles or sonic qualities as provided (e.g., 'haunting piano melodies providing a delicate counterpoint to a gritty, distorted lead guitar,' 'warm acoustic strumming forms the rhythmic backbone,' 'driving, punchy drum beat,' 'smooth, ethereal synth pads creating an atmospheric wash'). If the profile indicates few prominent instruments, focus on the overall sonic texture described (e.g., 'a sparse, minimalist arrangement' or 'a dense, layered sound').

4.  **Vocal Styling:** If the profile details vocal presence and characteristics, craft a description based on the provided gender/type, delivery style, and harmony information. Examples: 'features ethereal female soprano vocals with a breathy delivery,' 'a powerful male baritone lead, occasionally joined by tight backing harmonies,' 'a spoken-word narrative delivered with a calm intensity.' If vocals are described as absent or minimal, omit vocal descriptions in your output or explicitly state 'instrumental'.

5.  **Tempo and Rhythm Feel:** Translate the described tempo (BPM) and rhythmic characteristics into a description of the rhythmic feel. Examples from the profile like "syncopated bass" or "driving beat" should inform phrases like: 'a laid-back, shuffling groove,' 'an energetic, driving pulse,' 'a slow, deliberate and stately pace,' 'features complex, syncopated rhythms that create a sense of urgency.' You can include the BPM if it's a defining characteristic, e.g., "upbeat 140 BPM techno".

6.  **Structural and Dynamic Integration:** Subtly integrate the essence of the described song structure and dynamic profile into your overall description, rather than listing structural parts. For instance, if the analysis mentions "builds from quiet verses to an explosive chorus," you might write '...the piece gradually builds intensity from intimate verses into an expansive, anthemic chorus.' If a distinct instrumental solo is highlighted, you could mention '...highlighted by a searing mid-song guitar solo.' The aim is a flowing narrative reflecting the input description.

7.  **Evocative Language and Cohesion:** Weave all these elements into a single, cohesive, and engaging paragraph. Employ rich adjectives and adverbs, inspired by the descriptive terms in the input profile, to paint a vivid musical picture for Suno. The description should convey a distinct 'vibe' or 'atmosphere' as characterized in the source text. Strive for language that is both musically informative and creatively inspiring.

The final output MUST be a single paragraph. The total character count of this paragraph, including spaces and punctuation, MUST NOT exceed 1000 characters. Prioritize the most impactful musical descriptors from the provided profile to ensure conciseness while maintaining descriptive richness. Avoid filler words and be direct.

If the input profile itself indicates conflicting information or ambiguity for certain aspects, reflect that nuance if possible within the character limit, or prioritize the elements described with the most confidence or emphasis in the profile. Use your understanding of musical conventions to ensure the description is coherent and musically sensible based on the provided text.

Strive for a descriptive style similar to this example (though your content will be based on the input profile): 'A melancholic and atmospheric downtempo electronic track. It drifts on a slow, hypnotic beat, with deep sub-bass frequencies and shimmering, reverb-drenched synth pads creating a vast soundscape. Ethereal, wordless female vocal textures float above, adding to the introspective and slightly haunting mood. The piece evokes a sense of late-night contemplation in a rain-swept cityscape, with subtle dynamic shifts that prevent monotony without breaking the overall tranquil yet somber feel.'"""
        }
    }


def download_audio_from_youtube(url: str) -> Path:
    """
    Download audio from YouTube URL to a temporary file using yt-dlp.
    
    Args:
        url: YouTube URL
        
    Returns:
        Path to the downloaded audio file
    """
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Configure yt-dlp options for audio-only download
        ydl_opts = {
            'format': 'bestaudio[abr<=128]/best[abr<=128]',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': 60,
            'retries': 3,
            'fragment_retries': 3,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
                raise Exception("No file was downloaded")
                
            return downloaded_files[0]
        
    except Exception as e:
        raise Exception(f"Failed to download YouTube audio: {str(e)}")


def is_youtube_url(url: str) -> bool:
    """
    Check if a string is a YouTube URL.
    
    Args:
        url: String to check
        
    Returns:
        True if it's a YouTube URL, False otherwise
    """
    youtube_patterns = [
        r'(?:https?://)(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?://)(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
        r'(?:https?://)(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)',
        r'(?:https?://)(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]+)'
    ]
    
    return any(re.match(pattern, url) for pattern in youtube_patterns)


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
        "input", 
        nargs="?",
        help="Directory containing audio files to process, or YouTube URL"
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
        # Require input for processing
        if not args.input:
            parser.print_help()
            print("\nError: Directory or YouTube URL is required for processing audio files", file=sys.stderr)
            sys.exit(1)
            
        # Check if input is a YouTube URL or directory
        if is_youtube_url(args.input):
            # Process YouTube URL
            try:
                print(f"Downloading audio from YouTube URL: {args.input}")
                temp_audio_file = download_audio_from_youtube(args.input)
                print(f"Downloaded to: {temp_audio_file}")
                
                # Determine which prompt to use
                if args.prompt_type == "suno":
                    predefined_prompts = get_predefined_prompts()
                    step1_prompt = predefined_prompts["suno"]["step1"]
                    step2_prompt = predefined_prompts["suno"]["step2"]
                    print("Using predefined prompt: suno (two-step analysis)")
                    
                    step1_response, step2_response = process_audio_file_two_step(client, temp_audio_file, step1_prompt, step2_prompt)
                    
                    print(f"\n--- {temp_audio_file.name} ---")
                    print("=== DETAILED ANALYSIS ===")
                    print(step1_response)
                    print("\n=== SUNO STYLE PROMPT ===")
                    print(step2_response)
                    print("-" * (len(temp_audio_file.name) + 8))
                else:
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
                    
                    response = process_audio_file(client, temp_audio_file, prompt_to_use)
                    print(f"\n--- {temp_audio_file.name} ---")
                    print(response)
                    print("-" * (len(temp_audio_file.name) + 8))
                
                # Clean up temporary file
                temp_audio_file.unlink()
                temp_audio_file.parent.rmdir()
                
            except Exception as e:
                print(f"Error processing YouTube URL: {str(e)}", file=sys.stderr)
                sys.exit(1)
        else:
            # Process as directory
            directory_path = Path(args.input)
            if not directory_path.exists() or not directory_path.is_dir():
                print(f"Error: '{args.input}' is not a valid directory or YouTube URL", file=sys.stderr)
                sys.exit(1)
        
        # Check if using two-step suno prompt
        if args.prompt_type == "suno":
            predefined_prompts = get_predefined_prompts()
            step1_prompt = predefined_prompts["suno"]["step1"]
            step2_prompt = predefined_prompts["suno"]["step2"]
            print("Using predefined prompt: suno (two-step analysis)")
            
            results = process_directory_two_step(client, directory_path, step1_prompt, step2_prompt)
            
            # Output results for two-step processing
            if not results:
                print("No audio files found in the specified directory.")
                return
            
            for filename, (step1_response, step2_response) in results:
                print(f"\n--- {filename} ---")
                print("=== DETAILED ANALYSIS ===")
                print(step1_response)
                print("\n=== SUNO STYLE PROMPT ===")
                print(step2_response)
                print("-" * (len(filename) + 8))
        else:
            # Determine which prompt to use for single-step processing
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
                
            results = process_directory(client, directory_path, prompt_to_use)
            
            # Output results for single-step processing
            if not results:
                print("No audio files found in the specified directory.")
                return
            
            for filename, response in results:
                print(f"\n--- {filename} ---")
                print(response)
                print("-" * (len(filename) + 8))


if __name__ == "__main__":
    main()