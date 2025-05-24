# Gemini Music

Geminis audio functions are great. This is a simple interface to use them on the command line.
Since it has to upload the files to gemini it might take some time and cost some token. 
A command-line interface for processing audio files with Google's Gemini AI.

## Installation

```bash
# Install from the local directory
pip install -e .
```

## Configuration

### Method 1: Using .env file (Recommended)

Copy the sample environment file and add your API key:

```bash
cp .env.dist .env
```

Then edit `.env` and replace `your-google-api-key-here` with your actual Google API key:

```
GOOGLE_API_KEY=your-actual-api-key-here
```

### Method 2: Using environment variables

Alternatively, set your Google API key as an environment variable:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

## Usage

### Processing Local Audio Files

Run the CLI with a prompt and a directory containing audio files:

```bash
gemini-music "Describe this audio clip" /path/to/audio/files
```

### Processing YouTube URLs

You can also process audio directly from YouTube URLs:

```bash
# Process a YouTube video with a custom prompt
gemini-music "Analyze the musical elements" "https://www.youtube.com/watch?v=VIDEO_ID"

# Use predefined prompts with YouTube URLs
gemini-music --prompt-type analyze "https://www.youtube.com/watch?v=VIDEO_ID"
gemini-music --prompt-type suno "https://youtu.be/VIDEO_ID"
```

### Using Predefined Prompts

You can use built-in prompts for both local files and YouTube URLs:

```bash
# Use built-in analysis prompt
gemini-music --prompt-type analyze /path/to/audio/files

# Use built-in evaluation prompt  
gemini-music --prompt-type eval /path/to/audio/files

# Use Suno prompting for music generation
gemini-music --prompt-type suno /path/to/audio/files

# List all available predefined prompts
gemini-music --list-prompts
```

## Examples

### Local Audio Files

```bash
# Process all audio files in the current directory
gemini-music "Transcribe and summarize this audio" ./

# Process audio files in a specific directory
gemini-music "What genre of music is this?" ~/Music/samples

# Process a single audio file by creating a directory for it
mkdir -p single_file
cp my_audio.mp3 single_file/
gemini-music "Identify the instruments in this recording" single_file
```

### YouTube URLs

```bash
# Analyze a YouTube music video
gemini-music "What instruments can you hear?" "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Generate Suno prompts from YouTube videos
gemini-music --prompt-type suno "https://youtu.be/VIDEO_ID"

# Evaluate a song from YouTube
gemini-music --prompt-type eval "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Requirements

- Python 3.7+
- google-generativeai package
