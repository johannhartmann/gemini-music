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

Then run the CLI with a prompt and a directory containing audio files:

```bash
gemini-music "Describe this audio clip" /path/to/audio/files
```

You can also use predefined prompts:

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

## Requirements

- Python 3.7+
- google-generativeai package
