# Quick Setup Guide for CallScribe

Follow these steps to get CallScribe running on your MacBook Pro.

## Step 1: Install FFmpeg

```bash
brew install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

## Step 2: Install BlackHole (for System Audio)

BlackHole allows you to capture system audio (for Google Meet, phone calls, etc.):

```bash
brew install blackhole-2ch
```

## Step 3: Configure Multi-Output Device (macOS)

1. Open **Audio MIDI Setup**:
   - Go to Applications > Utilities > Audio MIDI Setup
   - Or use Spotlight: Cmd+Space, type "Audio MIDI Setup"

2. Create Multi-Output Device:
   - Click the **+** button in the bottom-left
   - Select **"Create Multi-Output Device"**

3. Configure the device:
   - Check **"BlackHole 2ch"**
   - Check your **built-in speakers** (so you can hear audio)
   - Right-click the Multi-Output Device and select "Use This Device For Sound Output"

4. Set System Output:
   - In macOS System Settings > Sound
   - Select the "Multi-Output Device" as your output

## Step 4: Set Up Python Environment

```bash
# Navigate to project
cd /Users/juancthomas/Documents/Development_projects/Python_projects/call_transcription

# Activate virtual environment
source venv/bin/activate

# Install dependencies (this may take a few minutes)
pip install -r requirements.txt
```

**Note:** The first `pip install` will download PyTorch and Whisper models (~500MB-1GB).

## Step 5: Configure API Key

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API key
nano .env
```

Add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
WHISPER_MODEL=base
SAMPLE_RATE=16000
CHANNELS=1
```

Get your API key from: https://console.anthropic.com/

Save and exit (Ctrl+X, then Y, then Enter)

## Step 6: Test Installation

### Test 1: List Audio Devices
```bash
python -m callscribe.main --list-devices
```

You should see BlackHole 2ch in the list. Note its device number.

### Test 2: Check Configuration
```bash
python -m callscribe.main --show-config
```

Verify your settings are correct.

### Test 3: Quick Recording Test (Microphone)
```bash
python -m callscribe.main --skip-analysis --timestamps
```

1. Press ENTER to start recording
2. Say something
3. Press ENTER to stop
4. You should see a transcript

### Test 4: Full Test with Analysis
```bash
python -m callscribe.main --timestamps --full-report
```

1. Press ENTER to start
2. Speak for 10-15 seconds
3. Press ENTER to stop
4. Wait for transcription and analysis
5. Check the `output/` folder for files

## Step 7: Record System Audio (Google Meet)

When you're on a Google Meet call:

```bash
# Use the BlackHole device number from --list-devices
# For example, if BlackHole is device 2:
python -m callscribe.main --device 2 --timestamps --full-report
```

1. Join your Google Meet call
2. Press ENTER in the terminal to start recording
3. Participate in the call
4. Press ENTER when done to stop and analyze

## Troubleshooting

### Can't hear audio during recording
- Make sure you selected the Multi-Output Device in System Settings
- Verify both BlackHole AND your speakers are checked in Audio MIDI Setup

### "No audio recorded"
- Check that BlackHole is receiving audio (open Audio MIDI Setup, watch the level meter)
- Try a different device number with `--device X`
- Test with microphone first (no --device flag)

### Whisper is slow
- Use a smaller model: `--model tiny` or `--model small`
- Your MacBook Pro should handle the `base` model fine
- For longer calls, consider using `tiny` for speed

### Module not found errors
- Make sure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## Quick Reference

```bash
# Activate environment
source venv/bin/activate

# Record with microphone (simple)
python -m callscribe.main

# Record system audio with timestamps
python -m callscribe.main --device 2 --timestamps

# Full report with saved audio
python -m callscribe.main --device 2 --timestamps --full-report --save-audio

# Skip AI analysis (faster, cheaper)
python -m callscribe.main --skip-analysis
```

## What Happens Next?

After successful recording:
- Transcript saved to `output/transcript_YYYYMMDD_HHMMSS.txt`
- Analysis saved to `output/analysis_YYYYMMDD_HHMMSS.md`
- Complete report saved to `output/report_YYYYMMDD_HHMMSS.md`
- Audio file (if --save-audio): `output/recording_YYYYMMDD_HHMMSS.wav`

## Cost Reminder

- Whisper transcription: FREE (runs locally)
- Claude analysis: ~$0.01-0.02 per hour of audio
- Total cost per 1-hour meeting: ~$0.01-0.02

You're all set! Enjoy using CallScribe!
