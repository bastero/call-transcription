# CallScribe - Quick Start Guide

Get CallScribe running in 5 minutes!

## Prerequisites Check

Make sure you have:
- [ ] Python 3.8+ installed
- [ ] Homebrew installed (for macOS)
- [ ] Anthropic API key (get from https://console.anthropic.com/)

## Quick Setup (5 Steps)

### 1. Install System Dependencies

```bash
# Install FFmpeg
brew install ffmpeg

# Install BlackHole (for system audio capture)
brew install blackhole-2ch
```

### 2. Install Python Dependencies

```bash
# Make sure you're in the project directory
cd /Users/juancthomas/Documents/Development_projects/Python_projects/call_transcription

# Activate virtual environment
source venv/bin/activate

# Install packages (this takes 2-3 minutes)
pip install -r requirements.txt
```

### 3. Configure API Key

```bash
# Copy example file
cp .env.example .env

# Edit and add your API key
nano .env
```

Change this line:
```
ANTHROPIC_API_KEY=your_api_key_here
```
to:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

Save: Ctrl+X, then Y, then Enter

### 4. Test Installation

```bash
python test_setup.py
```

All tests should pass!

### 5. First Recording

```bash
# Simple microphone test
python -m callscribe.main --timestamps
```

1. Press ENTER to start
2. Say: "Testing CallScribe, one two three"
3. Press ENTER to stop
4. Watch it transcribe and analyze!

## For Google Meet / System Audio

### One-Time Setup

1. Open **Audio MIDI Setup** (Cmd+Space, type "Audio MIDI")
2. Click **+** button → **Create Multi-Output Device**
3. Check both:
   - ✓ BlackHole 2ch
   - ✓ MacBook Pro Speakers
4. In **System Settings** → **Sound** → Select "Multi-Output Device"

### Recording a Call

```bash
# List devices to find BlackHole number
python -m callscribe.main --list-devices

# Start recording (replace 2 with your BlackHole device number)
python -m callscribe.main --device 2 --timestamps --full-report
```

1. Join your Google Meet call
2. Press ENTER in terminal to start recording
3. Have your meeting
4. Press ENTER when done
5. Wait for transcription and analysis
6. Check `output/` folder for results!

## Common Commands

```bash
# Activate environment (always do this first!)
source venv/bin/activate

# Simple microphone recording
python -m callscribe.main

# System audio with full report
python -m callscribe.main --device 2 --timestamps --full-report

# Skip analysis (faster)
python -m callscribe.main --skip-analysis

# Save audio file too
python -m callscribe.main --save-audio

# Use faster Whisper model
python -m callscribe.main --model tiny
```

## What Gets Created

After a recording, check the `output/` folder:
- `transcript_YYYYMMDD_HHMMSS.txt` - Your transcript
- `analysis_YYYYMMDD_HHMMSS.md` - Claude's analysis
- `report_YYYYMMDD_HHMMSS.md` - Complete report (if --full-report)
- `recording_YYYYMMDD_HHMMSS.wav` - Audio file (if --save-audio)

## Troubleshooting

**"No audio recorded"**
- Try microphone first (no --device flag)
- Check permissions in System Settings → Privacy & Security → Microphone

**"Can't hear during Google Meet"**
- Make sure Multi-Output Device is selected in Sound settings
- Both BlackHole and speakers should be checked in Audio MIDI Setup

**"Command not found"**
- Activate virtual environment: `source venv/bin/activate`
- Check you're in the right directory

**Whisper is slow**
- Use smaller model: `--model tiny` (much faster!)
- Your MacBook Pro should handle `base` fine though

## Tips

- First run downloads Whisper model (~140MB for base model)
- Use `--model tiny` for faster transcription
- Use `--skip-analysis` to save API costs during testing
- Always activate venv before running: `source venv/bin/activate`

## Next Steps

1. ✅ Test with microphone
2. ✅ Configure Multi-Output Device
3. ✅ Test with Google Meet
4. 🎯 Use it for real meetings!

For detailed docs, see:
- **SETUP.md** - Detailed setup instructions
- **README.md** - Full documentation
- **PYTHON_SCRIPT_PLAN.md** - Complete project plan

Happy transcribing! 🎙️
