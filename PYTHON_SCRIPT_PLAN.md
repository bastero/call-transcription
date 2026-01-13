# Call Transcription & Analysis - Python Script

## Project Name: CallScribe

## Overview
A local Python script that listens to system audio or microphone, transcribes conversations in real-time, identifies speakers, and uses Claude API to analyze the transcript for context, key points, and action items.

## Goal
Build a standalone Python application that can capture, transcribe, and intelligently analyze phone/video calls with minimal setup.

## Key Advantages Over Chrome Extension
- ✅ Works with ANY call platform (Zoom, Teams, Phone, Discord, etc.)
- ✅ No browser permissions needed
- ✅ Complete privacy - all processing local except Claude API
- ✅ Easier to develop and maintain
- ✅ Can run in background
- ✅ Direct integration with Claude API

## MVP Features

### Core Functionality
1. **Audio Capture**
   - Capture system audio (e.g., from speakers during a call)
   - OR capture microphone input
   - Real-time audio streaming

2. **Real-time Transcription**
   - Transcribe audio to text
   - Timestamp each utterance
   - Support continuous listening

3. **Speaker Diarization**
   - Identify different speakers
   - Label as Speaker 1, 2, 3, etc.
   - Optional: Allow manual speaker labeling

4. **Claude API Analysis**
   - Send transcript to Claude
   - Get intelligent analysis:
     - Meeting summary
     - Key discussion points
     - Action items with assignees
     - Context and insights
     - Sentiment/tone analysis
     - Follow-up recommendations

5. **Output**
   - Display live transcript in terminal
   - Save full transcript to file (TXT, JSON, Markdown)
   - Save Claude's analysis separately
   - Export in multiple formats

## Technology Stack

### Core Python Libraries

**Audio Capture:**
```python
# Option 1: PyAudio (cross-platform, microphone input)
import pyaudio

# Option 2: sounddevice (simpler API)
import sounddevice as sd

# Option 3: System audio capture (macOS/Windows specific)
# macOS: BlackHole + PyAudio
# Windows: PyAudioWPatch (captures system audio)
# Linux: PulseAudio/ALSA
```

**Transcription:**
```python
# Option 1: OpenAI Whisper (local, free, very accurate)
import whisper

# Option 2: OpenAI Whisper API (cloud, easier, costs $)
from openai import OpenAI

# Option 3: AssemblyAI (includes diarization)
import assemblyai as aai

# Option 4: Google Cloud Speech-to-Text
from google.cloud import speech
```

**Speaker Diarization:**
```python
# Option 1: pyannote.audio (local, free, good quality)
from pyannote.audio import Pipeline

# Option 2: AssemblyAI (if using their transcription)
# Included in API response

# Option 3: Simple VAD (Voice Activity Detection) + heuristics
# Not true diarization but can help
import webrtcvad
```

**Claude API Integration:**
```python
# Anthropic Python SDK
import anthropic
```

**Utilities:**
```python
import numpy as np          # Audio processing
import wave                 # WAV file handling
from datetime import datetime
import json                 # Export transcripts
import argparse             # CLI arguments
import threading            # Background processing
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│           CallScribe Application                │
│                                                 │
│  ┌──────────────┐      ┌──────────────┐        │
│  │    Audio     │─────▶│ Transcription│        │
│  │   Capture    │      │   Engine     │        │
│  │  (PyAudio/   │      │  (Whisper)   │        │
│  │ sounddevice) │      └──────┬───────┘        │
│  └──────────────┘             │                │
│                               ▼                │
│                    ┌──────────────────┐        │
│                    │    Speaker       │        │
│                    │   Diarization    │        │
│                    │  (pyannote)      │        │
│                    └──────┬───────────┘        │
│                           │                    │
│                           ▼                    │
│  ┌──────────────┐  ┌─────────────┐            │
│  │   Terminal   │◀─│  Transcript  │            │
│  │   Display    │  │   Manager    │            │
│  └──────────────┘  └──────┬───────┘            │
│                           │                    │
│  ┌──────────────┐         │                    │
│  │ File Export  │◀────────┘                    │
│  │(TXT/MD/JSON) │                              │
│  └──────────────┘                              │
└─────────────────────────────────────────────────┘
                    │
                    ▼
          ┌───────────────────┐
          │   Claude API      │
          │   (Analysis &     │
          │   Summarization)  │
          └───────────────────┘
```

## Recommended Tech Stack (Best Balance)

```python
# Audio Capture
sounddevice + numpy          # Cross-platform, easy to use

# Transcription
whisper (local)              # Free, runs on CPU/GPU, very accurate
# OR openai.audio.transcriptions (API) for easier setup

# Diarization
pyannote.audio               # Local, free, state-of-the-art
# Requires HuggingFace token (free)

# Analysis
anthropic                    # Claude API for intelligent analysis
```

## Implementation Phases

### Phase 1: Audio Capture (Days 1-2)
- [ ] Set up Python environment
- [ ] Install audio libraries (sounddevice/PyAudio)
- [ ] Test microphone capture
- [ ] Implement real-time audio recording
- [ ] Save audio to WAV file
- [ ] Test with 30-second recording

**Deliverable:** Script that records audio and saves to file

### Phase 2: Basic Transcription (Days 3-4)
- [ ] Install Whisper (local or API)
- [ ] Transcribe saved audio files
- [ ] Display transcript in terminal
- [ ] Add timestamps to transcript
- [ ] Test accuracy with different audio sources

**Deliverable:** Script that records and transcribes audio

### Phase 3: Real-time Streaming (Days 5-7)
- [ ] Implement chunked audio processing
- [ ] Stream audio to Whisper in real-time
- [ ] Display transcript as it's generated
- [ ] Handle audio buffering
- [ ] Optimize for low latency

**Deliverable:** Real-time transcription working

### Phase 4: Speaker Diarization (Days 8-10)
- [ ] Integrate pyannote.audio
- [ ] Process audio for speaker segments
- [ ] Align speakers with transcript
- [ ] Display speaker labels (Speaker 1, 2, etc.)
- [ ] Optional: Manual speaker naming interface

**Deliverable:** Transcript with speaker identification

### Phase 5: Claude API Integration (Days 11-13)
- [ ] Set up Anthropic API key
- [ ] Create prompt templates for analysis
- [ ] Send transcript to Claude after call ends
- [ ] Parse Claude's response
- [ ] Display analysis in terminal

**Prompt templates:**
- Meeting summary
- Action items extraction
- Key decisions identification
- Context and insights
- Follow-up suggestions

**Deliverable:** Full analysis powered by Claude

### Phase 6: File Export & UX (Days 14-15)
- [ ] Export transcript (TXT, Markdown, JSON)
- [ ] Export Claude analysis separately
- [ ] Add CLI arguments (--output, --format, etc.)
- [ ] Improve terminal UI (colors, formatting)
- [ ] Add start/stop controls (keyboard shortcuts)
- [ ] Error handling and logging

**Deliverable:** Polished, usable tool

### Phase 7: Optimization & Features (Days 16-20)
- [ ] Optimize memory usage for long calls
- [ ] Add configuration file support
- [ ] Implement pause/resume
- [ ] Add real-time Claude streaming (optional)
- [ ] Create installation script
- [ ] Write documentation

**Deliverable:** Production-ready tool

## File Structure

```
callscribe/
├── README.md
├── requirements.txt
├── setup.py
├── config.yaml
├── .env.example
├── callscribe/
│   ├── __init__.py
│   ├── main.py
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── capture.py          # Audio capture logic
│   │   └── preprocessor.py     # Audio preprocessing
│   ├── transcription/
│   │   ├── __init__.py
│   │   ├── whisper_client.py   # Whisper integration
│   │   └── diarization.py      # Speaker diarization
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── claude_client.py    # Claude API integration
│   │   └── prompts.py          # Prompt templates
│   ├── output/
│   │   ├── __init__.py
│   │   ├── terminal.py         # Terminal display
│   │   └── exporter.py         # File export
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # Configuration management
│       └── logger.py           # Logging setup
├── tests/
│   ├── test_audio.py
│   ├── test_transcription.py
│   └── test_analysis.py
└── examples/
    ├── sample_transcript.txt
    └── sample_analysis.md
```

## Installation & Setup

### Prerequisites
```bash
# Python 3.8+
python --version

# FFmpeg (required by Whisper)
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/
```

### Installation
```bash
# Clone repo
git clone https://github.com/yourusername/callscribe.git
cd callscribe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Download models (if using local Whisper)
python -c "import whisper; whisper.load_model('base')"

# Download diarization model (requires HuggingFace token)
# Get token from: https://huggingface.co/settings/tokens
```

### Requirements.txt
```
# Audio
sounddevice>=0.4.6
numpy>=1.24.0
wave

# Transcription
openai-whisper>=20231117  # Local Whisper
# OR
openai>=1.0.0            # Whisper API

# Diarization
pyannote.audio>=3.1.0
torch>=2.0.0

# Analysis
anthropic>=0.18.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0
colorama>=0.4.6         # Terminal colors
rich>=13.0.0            # Better terminal UI

# Optional
pydub>=0.25.0           # Audio file manipulation
```

## Usage

### Basic Usage
```bash
# Start recording and transcribing
python -m callscribe

# With specific output file
python -m callscribe --output meeting_2024_01_10.txt

# With different Whisper model
python -m callscribe --model medium

# Export as JSON
python -m callscribe --format json

# Quiet mode (no terminal output, just save to file)
python -m callscribe --quiet --output transcript.txt
```

### Configuration (config.yaml)
```yaml
audio:
  sample_rate: 16000
  channels: 1
  device: null  # Auto-detect
  chunk_duration: 5  # seconds

transcription:
  engine: "whisper"  # or "openai-api"
  model: "base"      # tiny, base, small, medium, large
  language: "en"

diarization:
  enabled: true
  min_speakers: 2
  max_speakers: 10

analysis:
  provider: "claude"
  model: "claude-3-5-sonnet-20241022"
  auto_analyze: true  # Analyze after call ends
  realtime: false     # Stream analysis during call

output:
  format: "markdown"  # txt, json, markdown
  include_timestamps: true
  save_audio: false
```

## Claude Analysis Prompts

### Prompt Template for Meeting Analysis
```python
ANALYSIS_PROMPT = """
I have a transcript from a meeting/call. Please analyze it and provide:

1. **Meeting Summary** (2-3 sentences)
   - What was the overall purpose and outcome?

2. **Key Discussion Points**
   - List the main topics discussed
   - Include important decisions made

3. **Action Items**
   - Extract specific tasks mentioned
   - Identify who is responsible (if mentioned)
   - Note any deadlines

4. **Context & Insights**
   - Important context or background mentioned
   - Notable concerns or risks raised
   - Opportunities identified

5. **Follow-up Recommendations**
   - What should happen next?
   - Any unresolved questions?

Here's the transcript:

{transcript}

Please be specific and reference the speakers when relevant.
"""
```

### Advanced Analysis Options
```python
# Sentiment analysis
SENTIMENT_PROMPT = """
Analyze the sentiment and tone of this conversation:
- Overall mood (positive, neutral, negative, mixed)
- Each speaker's engagement level
- Any tension or disagreement
- Collaborative vs. combative dynamics
"""

# Technical analysis
TECHNICAL_PROMPT = """
Extract technical details from this conversation:
- Technical decisions made
- Architecture or design choices discussed
- Technologies mentioned
- Technical challenges or blockers
"""

# Sales/Business analysis
BUSINESS_PROMPT = """
Analyze this call from a business perspective:
- Customer pain points mentioned
- Budget/pricing discussions
- Timeline and urgency
- Competitors mentioned
- Next steps in sales process
"""
```

## Cost Estimates

### API Costs (Per Hour of Audio)

**Whisper API (OpenAI):**
- $0.006 per minute
- 60 minutes = $0.36 per hour

**AssemblyAI (Transcription + Diarization):**
- $0.00025 per second
- 3600 seconds = $0.90 per hour

**Claude API (Analysis):**
- ~5,000-10,000 input tokens per hour transcript
- ~1,000-2,000 output tokens
- Claude Sonnet: ~$0.05-0.10 per hour
- Claude Haiku: ~$0.01-0.02 per hour (cheaper option)

**Total Cost (API-based):**
- ~$0.42-$1.02 per hour of meeting

**Local Whisper + pyannote:**
- $0.01-0.02 per hour (Claude API only)
- FREE if you skip Claude analysis

## Privacy & Legal Considerations

### Recording Consent
- **⚠️ CRITICAL**: Recording conversations may require consent
- **Two-party consent states**: CA, FL, PA, and others require ALL parties to consent
- **One-party consent**: Most states allow recording if you're a participant
- **International**: GDPR, other laws may apply

### Best Practices
1. Always announce when recording starts
2. Get explicit verbal consent from all participants
3. Store recordings securely
4. Delete recordings after processing (if not needed)
5. Don't share transcripts without permission

### Disclaimer to Add
```
⚠️  WARNING: This tool records and transcribes conversations.
Ensure you have proper consent from all participants before recording.
Recording laws vary by jurisdiction - know your local laws.
```

## Technical Challenges & Solutions

### Challenge 1: System Audio Capture
**Problem**: Capturing system audio (what you hear) is platform-specific

**Solutions:**
- **macOS**: Use BlackHole virtual audio device + PyAudio
- **Windows**: Use PyAudioWPatch (fork that supports WASAPI loopback)
- **Linux**: PulseAudio monitor source
- **Fallback**: Capture microphone (picks up both sides if on speaker)

### Challenge 2: Real-time Processing Performance
**Problem**: Whisper can be slow on CPU, causing lag

**Solutions:**
- Use smaller Whisper model (base or small)
- Process in chunks (5-10 seconds)
- Use GPU acceleration if available
- Consider Whisper API for lower latency
- Use faster-whisper (optimized implementation)

### Challenge 3: Speaker Diarization Accuracy
**Problem**: Distinguishing speakers is hard, especially with background noise

**Solutions:**
- Use high-quality audio input
- Limit to 2-4 speakers for better accuracy
- Allow manual correction of speaker labels
- Consider using AssemblyAI for better diarization
- Pre-process audio (noise reduction)

### Challenge 4: Long Meetings Memory Usage
**Problem**: Hour-long meetings = lots of audio data in memory

**Solutions:**
- Process and discard audio chunks after transcription
- Stream to disk instead of keeping in RAM
- Use generators instead of loading full audio
- Implement rolling buffer

## Alternative Implementations

### Minimal Version (Quickest Start)
```python
# Just 3 files, uses APIs for everything
audio_recorder.py       # sounddevice → save WAV
transcriber.py          # OpenAI Whisper API
analyzer.py            # Claude API

# Total: ~200 lines of code
# Cost: ~$0.50/hour
# Setup time: 30 minutes
```

### Privacy-First Version (All Local)
```python
# No external APIs except optional Claude
local_whisper.py       # whisper.cpp (faster local)
local_diarization.py   # pyannote.audio
optional_analysis.py   # Call Claude or use local LLM

# Cost: $0 (or ~$0.02/hour if using Claude)
# Requires: Better hardware (GPU recommended)
```

### Enterprise Version (Full Features)
```python
# Production-ready with all features
- Real-time streaming UI
- Multi-speaker identification
- Integration with calendar
- Automatic meeting detection
- Cloud storage sync
- Team collaboration features
```

## Next Steps

### Option A: Quick Prototype (2-3 days)
1. Set up Python environment
2. Record audio with sounddevice
3. Transcribe with Whisper API
4. Analyze with Claude API
5. Done!

### Option B: Full-Featured Tool (2-3 weeks)
Follow the full implementation phases above

### Option C: Let's Start Together
I can help you:
1. Set up the project structure
2. Write the audio capture module
3. Integrate Whisper
4. Create Claude prompts
5. Build the complete tool step-by-step

## Getting Started Checklist

- [ ] Install Python 3.8+
- [ ] Install FFmpeg
- [ ] Get Anthropic API key
- [ ] Decide: Local Whisper or API?
- [ ] Decide: Speaker diarization needed?
- [ ] Test audio capture on your system
- [ ] Check recording laws in your jurisdiction

## Example Output

```markdown
# Meeting Transcript
Date: 2024-01-10 14:30:00
Duration: 45 minutes
Speakers: 3

## Transcript

[00:00:05] Speaker 1: Hi everyone, thanks for joining. Let's discuss the Q1 roadmap.

[00:00:12] Speaker 2: Sounds good. I think we should prioritize the mobile app.

[00:00:18] Speaker 3: Agreed, but we need to resolve the API performance issues first.

...

---

# Claude's Analysis

## Meeting Summary
Team discussed Q1 priorities, focusing on mobile app development and API performance improvements. Decision made to allocate 2 engineers to API optimization before mobile work begins.

## Key Discussion Points
- Mobile app is top priority for Q1
- API currently has latency issues affecting user experience
- Need to hire additional backend engineer
- Timeline: API fixes by end of January, mobile development starts February

## Action Items
- **Speaker 3**: Investigate API performance issues (Due: Jan 15)
- **Speaker 1**: Draft job description for backend engineer (Due: Jan 12)
- **Speaker 2**: Create mobile app mockups (Due: Jan 20)

## Context & Insights
- Customer complaints about slow load times drove this prioritization
- Team is understaffed for Q1 goals
- Risk: Timeline might slip if API issues are more complex than expected

## Follow-up Recommendations
- Schedule follow-up on Jan 15 to review API investigation
- Begin recruiting process immediately
- Consider pushing mobile timeline if API work takes longer
```

This is much more achievable than a Chrome extension and gives you more control!
