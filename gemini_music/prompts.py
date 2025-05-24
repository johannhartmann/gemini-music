"""Prompt definitions for Gemini Music analysis."""

from typing import Dict, Union
from .config import PromptType


class PromptManager:
    """Manages predefined prompts for audio analysis."""
    
    @staticmethod
    def get_prompts() -> Dict[str, Union[str, Dict[str, str]]]:
        """Returns a dictionary of predefined prompts for various audio analysis tasks."""
        return {
            PromptType.ANALYZE.value: PromptManager._get_analyze_prompt(),
            PromptType.EVAL.value: PromptManager._get_eval_prompt(),
            PromptType.SUNO.value: PromptManager._get_suno_prompts(),
        }
    
    @staticmethod
    def get_prompt(prompt_type: PromptType) -> Union[str, Dict[str, str]]:
        """Get a specific prompt by type."""
        prompts = PromptManager.get_prompts()
        return prompts[prompt_type.value]
    
    @staticmethod
    def get_default_prompt() -> str:
        """Returns the default detailed prompt for music analysis."""
        return PromptManager._get_analyze_prompt()
    
    @staticmethod
    def _get_analyze_prompt() -> str:
        """Comprehensive 10-section musical analysis prompt."""
        return """Provide an extremely detailed and comprehensive musical analysis of this audio, addressing all of the following aspects:

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

Present this analysis in a clear, organized format with section headings. Prioritize accuracy, detail, and musical insight. Be specific rather than general, providing exact musical terminology where appropriate."""

    @staticmethod
    def _get_eval_prompt() -> str:
        """Pop song evaluation system prompt."""
        return """You are MusicEvalBot, a specialist AI for analyzing and evaluating pop-song recordings.  
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

    @staticmethod
    def _get_suno_prompts() -> Dict[str, str]:
        """Two-step Suno AI prompts."""
        return {
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

**CRITICAL: EMPHASIZE DISTINCTIVE ELEMENTS TO AVOID MAINSTREAM MUZAK**
Your description must prioritize what makes this music UNIQUE and DIFFERENT from generic mainstream music. Pay special attention to:
- Unconventional instruments or sounds mentioned in the analysis
- Specific processing effects, distortion, or unusual timbres
- Non-standard chord progressions or harmonic approaches
- Distinctive rhythmic patterns or time signatures
- Unique vocal techniques or delivery styles
- Any experimental or non-commercial elements
- Specific cultural or era references that distinguish the sound

You will be provided with a detailed textual musical profile. This profile will describe various aspects of the music, such as:
* Core Musical Attributes: Tempo (BPM), Key & Mode, Time Signature, Overall Energy Level.
* Genre and Style: Primary and secondary genres, stylistic descriptors.
* Mood and Atmosphere: Dominant moods and atmospheric qualities.
* Instrumentation and Timbre: Predominant instruments with their roles, timbral characteristics, playing styles, and any notable effects.
* Vocal Characteristics (if applicable): Vocal presence, type/gender, delivery style, lyrical themes (if inferable), and harmonies.
* Structure and Dynamics: Overall song structure, key sections, dynamic profile, and rhythmic feel.
* Production and Sonic Quality: Production style, soundstage/mix, and unique sonic signatures.

Your transformation logic should be as follows, drawing from the provided textual profile:

1.  **Genre Synthesis:** From the described genres, identify the primary genre(s). If one genre is clearly dominant, feature it prominently. If multiple genres are highlighted as significant, attempt to describe a blend or fusion (e.g., 'a compelling fusion of synthwave and dark ambient elements,' or 'an indie rock track with strong folk influences'). **If the analysis mentions specific influential eras (e.g., '80s vibe,' 'classic 70s rock feel') or named stylistic leanings (e.g., 'New Wave character,' 'Motown rhythm section') that are central to the track's identity, try to weave these terms directly and concisely into your description.**

2.  **Mood Articulation & Evocative Imagery:** Synthesize information from the described moods, key/mode, tempo, and energy level to articulate the dominant mood(s). Use evocative adjectives. **Crucially, if the analysis provides distinct, concise, and highly evocative imagery or scenarios (e.g., 'rain-slicked city at night drive,' 'vast desert landscape at dawn,' 'intimate candlelit performance'), try to incorporate a distilled essence of this imagery directly, as it can be very effective for Suno. Focus on imagery that powerfully encapsulates the mood.**

3.  **Instrumentation Description:** Based on the listed instruments and their characteristics, describe the core instrumentation. Use vivid adjectives. **CRITICAL: Always mention any acoustic instruments, real drums, electric guitars with specific effects (distortion, overdrive, delay), analog synthesizers, or unconventional instruments identified in the analysis. These distinctive elements prevent Suno from defaulting to generic electronic sounds. Emphasize unique instrumental roles if highlighted in the analysis (e.g., 'heavily distorted electric guitar layers,' 'analog Moog bass with filter sweeps,' 'live drum kit with room reverb,' 'processed acoustic guitar arpeggios'). Specify characteristic timbres that distinguish the sound from typical mainstream production.**

4.  **Vocal Styling:** If the profile details vocal presence and characteristics, craft a description based on the provided gender/type, delivery style, and harmony information. Examples: 'features ethereal female soprano vocals with a breathy delivery,' 'a powerful male baritone lead, occasionally joined by tight backing harmonies,' 'a spoken-word narrative delivered with a calm intensity.' If vocals are described as absent or minimal, omit vocal descriptions or explicitly state 'instrumental'.

5.  **Tempo and Rhythm Feel:** Translate the described tempo (BPM) and rhythmic characteristics into a description of the rhythmic feel. (e.g., 'a laid-back, shuffling groove,' 'an energetic, driving 130 BPM pulse,' 'slow, deliberate pace,' 'complex, syncopated rhythms'). **If specific drum sounds are highlighted as character-defining (e.g., 'booming 808s', 'crisp LinnDrum pattern', 'live acoustic drums', 'compressed room sound'), mention them briefly.**

6.  **Structural and Dynamic Integration:** Subtly integrate the essence of the described song structure and dynamic profile. **Instead of listing parts, aim to convey the overall emotional or energetic journey if the analysis describes a clear arc (e.g., 'builds from sparse intimacy to an epic, layered chorus,' 'features introspective verses contrasting with powerful, uplifting refrains,' or 'maintains a consistent high-energy drive with brief, impactful breakdowns').**

7.  **Distinctive Elements Priority:** **MOST IMPORTANT: Before finalizing your description, review the analysis for any elements that distinguish this music from typical mainstream pop/rock/electronic music. These might include: unusual time signatures, specific vintage equipment mentioned, cultural influences, experimental techniques, or distinctive production choices. These elements must be preserved in your description to prevent Suno from generating generic music.**

8.  **Evocative Language and Cohesion:** Weave all these elements into a single, cohesive, and engaging paragraph. Employ rich adjectives and adverbs, inspired by the descriptive terms in the input profile, to paint a vivid musical picture for Suno. The description should convey a distinct 'vibe' or 'atmosphere' as characterized in the source text. Strive for language that is both musically informative and creatively inspiring.

The final output MUST be a single paragraph. The total character count of this paragraph, including spaces and punctuation, MUST NOT exceed 1000 characters. Prioritize the most impactful musical descriptors from the provided profile to ensure conciseness while maintaining descriptive richness. Avoid filler words and be direct.

If the input profile itself indicates conflicting information or ambiguity for certain aspects, reflect that nuance if possible within the character limit, or prioritize the elements described with the most confidence or emphasis in the profile. Use your understanding of musical conventions to ensure the description is coherent and musically sensible based on the provided text.""",
            "step3": """You are an expert songwriter and lyricist, tasked with creating a detailed template prompt for generating lyrics in the Suno AI format. Based on the provided musical analysis, your goal is to write a comprehensive prompt template that would guide someone to create lyrics matching the style, mood, and characteristics of the analyzed song while incorporating any topic they choose.

You will be provided with a comprehensive musical analysis that includes genre, mood, vocal characteristics, song structure, lyrical themes, and overall atmosphere. Based on this analysis, create a detailed prompt template for lyrics generation that includes placeholders for the user to specify their own topic.

The generated prompt should be a ready-to-use template where users can insert their chosen topic and get appropriate lyrics guidance.

**LANGUAGE PRESERVATION:**
- FIRST, identify the language of the original lyrics from the musical analysis
- The generated lyrics template MUST specify that lyrics should be written in the SAME LANGUAGE as the original song
- If the original song contains multiple languages, note this and specify the primary language for the template
- If the language cannot be determined from the analysis, default to English but note this uncertainty

**CRITICAL SUNO FORMATTING RULES (include these in your generated prompt):**
- `[Square brackets]` - ALL musical instructions, structure tags, vocal directions, and comments
- `(Parentheses)` - ONLY for sung content like ad-libs, backing vocals, or choir parts
- NEVER use parentheses for musical instructions or comments - they will be sung!

**AVOID AI CLICHES (include this warning in your generated prompt):**
- Avoid overused AI phrases like: "neon lights", "concrete jungle", "shadows dance", "echoes fade", "digital dreams", "silicon soul", "electric pulse", "chrome and steel", "virtual reality", "algorithmic heart"
- Avoid generic metaphors: "phoenix rising", "broken wings", "shattered glass", "diamonds in the rough", "fire in your eyes", "storm in my heart"
- Use specific, authentic imagery that fits the genre and era instead of generic AI-generated phrases
- Focus on concrete, relatable experiences rather than abstract technological metaphors

**Your Task:**
Analyze the musical profile and create a structured prompt that specifies:

1. **Topic Integration:**
   - How to incorporate the given TOPIC into the song's style and mood
   - Approach the topic in a way that fits the identified genre conventions
   - Adapt the topic to match the emotional tone of the analysis

2. **Vocal Characteristics & Style:**
   - Specify vocal gender and style (e.g., "Male vocals with a raspy, emotional delivery")
   - Delivery approach (sung, rapped, spoken, whispered, etc.)
   - Vocal intensity and energy level
   - Any special vocal techniques mentioned

3. **Song Structure & Format:**
   - Recommended song structure based on the analysis
   - Suno formatting tags to use ([Intro], [Verse], [Chorus], [Bridge], [Outro], etc.)
   - Placement of instrumental sections
   - Any special structural elements from the analysis

4. **Lyrical Content & Themes:**
   - How to weave the TOPIC into the thematic content
   - Emotional tone and atmosphere to convey while addressing the topic
   - Vocabulary style and complexity level appropriate for both genre and topic
   - Subject matter approach that merges the topic with genre conventions
   - Narrative perspective (first person, storytelling, etc.) that serves the topic

5. **Mood & Atmosphere:**
   - Overall emotional feeling to capture while exploring the topic
   - Energy level throughout the song
   - Any dynamic changes or emotional arcs related to the topic development
   - Specific imagery or scenarios that connect the topic to the song's mood

6. **Genre-Specific Elements:**
   - Lyrical conventions typical of the identified genre applied to the topic
   - Cultural references or stylistic elements that support the topic
   - Language style and word choices appropriate for both genre and topic
   - Any era-specific lyrical approaches adapted for the topic

**Output Format:**
Create a comprehensive prompt that could be given to a lyricist, structured as clear instructions. The prompt should specify how to write about the given TOPIC in the style of the analyzed song. The prompt should be detailed enough that someone could write appropriate topic-focused lyrics without hearing the original song.

**Example Output Structure:**
"Write lyrics about [YOUR TOPIC HERE] for a [genre] song with [vocal style]. The song should follow this structure: [structure]. The lyrics should explore this topic while conveying [mood/themes] and using [style elements]. Approach the subject from a [perspective] that fits the [genre] style. Vocal delivery should be [delivery style]. 

LANGUAGE REQUIREMENT:
- Write the lyrics in [DETECTED LANGUAGE] to match the original song's language
- Maintain authentic vocabulary and expressions native to this language
- Use cultural references and idioms appropriate for [DETECTED LANGUAGE] speakers

FORMATTING RULES:
- Use [square brackets] for ALL musical instructions: [Verse], [Chorus], [Male Vocals], [Whisper], etc.
- Use (parentheses) ONLY for sung ad-libs or backing vocals: (yeah!), (ooh-ah), (echo this line)
- NEVER put musical instructions in parentheses - they will be sung instead of followed

AVOID AI CLICHES:
- NO overused phrases: 'neon lights', 'concrete jungle', 'shadows dance', 'echoes fade', 'digital dreams'
- NO generic metaphors: 'phoenix rising', 'broken wings', 'fire in your eyes', 'storm in my heart'
- Use authentic, genre-specific imagery and relatable human experiences
- Write with genuine emotion and specific details, not abstract AI-generated concepts

Include these Suno formatting elements: [specific tags]. The overall tone should be [atmosphere] with the theme developed through [approach]."

Make the prompt specific and actionable, with ONE clear placeholder [YOUR TOPIC HERE] at the beginning where the user can insert their chosen topic. After that, refer to it as 'this topic', 'the subject', 'the theme', etc. 

**CRITICAL REQUIREMENTS FOR YOUR GENERATED TEMPLATE:**
1. MUST include language specification based on the detected language from the analysis
2. MUST include the formatting rules to prevent users from incorrectly using parentheses for musical instructions
3. MUST include anti-cliche guidelines to ensure authentic, genre-appropriate lyrics
4. Should specify the exact language detected (e.g., "Write the lyrics in Spanish", "Write the lyrics in French", etc.)"""
        }