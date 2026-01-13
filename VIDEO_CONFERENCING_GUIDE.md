# Video Conferencing Guide

## Overview

CallScribe now supports **dual-stream recording** for video conferencing applications like Zoom, Google Meet, Microsoft Teams, and more. This feature captures both your voice (microphone) and remote participants (system audio) simultaneously, creating a complete transcript of your video calls.

## Features

### 🎯 Automatic Detection
- Detects running video conferencing apps (Zoom, Meet, Teams, WebEx, Discord, Slack, Skype)
- Shows app-specific setup instructions
- Verifies BlackHole installation automatically

### 🎙️ Dual-Stream Recording
- **Microphone Stream**: Captures your voice
- **System Audio Stream**: Captures remote participants via BlackHole
- **Combined Output**: Mixes both streams for complete transcription

### 🌐 Multiple Interfaces
- **Web GUI**: Point-and-click video conference mode toggle
- **CLI**: Command-line video conference mode with `--video-conference`

## Prerequisites

### 1. Install BlackHole

BlackHole is a virtual audio device that captures system audio on macOS.

```bash
brew install blackhole-2ch
```

**Verify Installation:**
```bash
# Using CLI
python -m callscribe.main --detect-video-apps

# Or check manually
brew list blackhole-2ch
```

### 2. Create Multi-Output Device

This allows you to hear audio while CallScribe records it.

**Steps:**
1. Open **Audio MIDI Setup** (Applications > Utilities > Audio MIDI Setup)
2. Click the **+** button (bottom-left)
3. Select **"Create Multi-Output Device"**
4. In the right panel, check both:
   - ✅ **BlackHole 2ch**
   - ✅ **Your Speakers/Headphones**
5. Right-click the Multi-Output Device → **"Use This Device For Sound Output"** (optional)

**Important:** Do NOT add your microphone to the Multi-Output Device!

### 3. Configure Your Video App

Each video app needs to be configured to use the Multi-Output Device for audio output while keeping your regular microphone for input.

## Setup Instructions by Application

### Zoom

1. **In Zoom Settings (Audio):**
   - Speaker: **Multi-Output Device**
   - Microphone: **Your actual microphone** (Built-in Microphone, USB mic, etc.)

2. **In CallScribe:**
   - Web GUI: Enable "Video Conference Mode" toggle
   - CLI: Use `--video-conference` flag

3. **Start Recording** in CallScribe BEFORE or DURING your Zoom meeting

### Google Meet (Chrome)

1. **In Meet Settings (Audio):**
   - Speakers: **Multi-Output Device**
   - Microphone: **Your actual microphone**

2. **Or set system-wide:**
   - System Preferences → Sound → Output: **Multi-Output Device**
   - Chrome will use system audio settings

3. **In CallScribe:**
   - Enable "Video Conference Mode"

### Microsoft Teams

1. **In Teams Settings (Devices):**
   - Speaker: **Multi-Output Device**
   - Microphone: **Your actual microphone**

2. **In CallScribe:**
   - Enable "Video Conference Mode"

### Discord

1. **In Discord Settings (Voice & Video):**
   - Output Device: **Multi-Output Device**
   - Input Device: **Your actual microphone**

2. **In CallScribe:**
   - Enable "Video Conference Mode"

### Slack

1. **In Slack Settings (Audio & video):**
   - Speaker: **Multi-Output Device**
   - Microphone: **Your actual microphone**

2. **In CallScribe:**
   - Enable "Video Conference Mode"

## Using Video Conference Mode

### Web GUI Method

1. **Launch CallScribe Web GUI:**
   ```bash
   python -m callscribe gui
   ```

2. **Check Detection:**
   - If video apps are running, you'll see a banner: "📹 Video Conference Apps Detected"
   - Shows which apps are detected (e.g., "Zoom, Google Meet")

3. **Enable Video Conference Mode:**
   - Expand "Options" panel
   - Toggle ON: **"Video Conference Mode"**

4. **Start Recording:**
   - Select recording mode (Standard, Streaming, or Pausable)
   - Click **Start**
   - Join or continue your video call
   - Click **Stop** when meeting ends

5. **View Results:**
   - Transcript appears automatically
   - If "Full Report" enabled, Claude analysis displays

### CLI Method

1. **Detect Video Apps (Optional):**
   ```bash
   python -m callscribe.main --detect-video-apps
   ```

   Shows:
   - Detected video apps
   - BlackHole installation status
   - Setup instructions

2. **Start Recording:**
   ```bash
   # Basic video conference recording
   python -m callscribe.main --video-conference

   # With specific devices
   python -m callscribe.main --video-conference --device 0 --system-device 2

   # With Claude analysis
   python -m callscribe.main --video-conference --full-report

   # Save audio files
   python -m callscribe.main --video-conference --save-audio
   ```

3. **Recording Process:**
   - CallScribe shows detected apps and device status
   - Press ENTER to start
   - Have your video call
   - Press ENTER to stop

4. **Output:**
   - `transcript_YYYYMMDD_HHMMSS.txt` - Complete transcript
   - `analysis_YYYYMMDD_HHMMSS.md` - Claude analysis (if enabled)
   - `recording_YYYYMMDD_HHMMSS_combined.wav` - Mixed audio
   - `recording_YYYYMMDD_HHMMSS_mic.wav` - Your voice only
   - `recording_YYYYMMDD_HHMMSS_system.wav` - Remote participants only

## CLI Options

### Video Conference Options

```bash
--video-conference          Enable dual-stream mode
--system-device ID          BlackHole device ID (auto-detected if omitted)
--detect-video-apps         Show detected apps and setup instructions
--device ID                 Microphone device ID (see --list-devices)
```

### General Options

```bash
--list-devices             List all audio devices
--model MODEL              Whisper model (tiny, base, small, medium, large)
--save-audio               Save audio files (3 files: combined, mic, system)
--full-report              Generate Claude analysis
--skip-analysis            Skip Claude analysis
--timestamps               Add timestamps to transcript
--output FILENAME          Custom output filename
--output-dir DIR           Output directory (default: output/)
```

### Example Commands

```bash
# Quick video call recording
python -m callscribe.main --video-conference

# High-quality with analysis
python -m callscribe.main --video-conference --model medium --full-report

# Save all audio streams
python -m callscribe.main --video-conference --save-audio

# Custom devices
python -m callscribe.main --video-conference --device 1 --system-device 3

# Check setup before recording
python -m callscribe.main --detect-video-apps
```

## How It Works

### Dual-Stream Architecture

```
┌─────────────────┐
│  Your Voice     │──► Microphone ──────────────┐
└─────────────────┘                             │
                                                 ▼
┌─────────────────┐                     ┌──────────────┐
│  Remote Voices  │──► System Audio ──► │  CallScribe  │
└─────────────────┘     (BlackHole)     │  Dual-Stream │
                                         │   Capture    │
                    Multi-Output         └──────────────┘
                    Device allows                │
                    you to hear                  ▼
                    while recording      ┌──────────────┐
                                        │   Combined    │
                                        │   Audio Mix   │
                                        └──────────────┘
                                                 │
                                                 ▼
                                        ┌──────────────┐
                                        │   Whisper    │
                                        │Transcription │
                                        └──────────────┘
```

### Recording Process

1. **Initialization:**
   - Detects BlackHole device automatically
   - Uses default microphone (or specified with `--device`)
   - Validates both audio streams are available

2. **Capture:**
   - Records from microphone and BlackHole simultaneously
   - Buffers audio chunks from both streams
   - Synchronizes timing automatically

3. **Processing:**
   - Combines both audio streams (averaging/mixing)
   - Ensures same length (pads shorter stream if needed)
   - Transcribes combined audio with Whisper

4. **Output:**
   - Saves combined transcript
   - Optionally saves separate audio files
   - Runs Claude analysis if enabled

## Troubleshooting

### "BlackHole not found"

**Problem:** CallScribe can't find BlackHole device

**Solution:**
```bash
# Install BlackHole
brew install blackhole-2ch

# Verify installation
python -m callscribe.main --detect-video-apps

# List devices to see BlackHole
python -m callscribe.main --list-devices
```

### "No audio recorded" or Transcript is empty

**Problem:** Recording completes but no audio captured

**Possible Causes:**
1. Video app not set to Multi-Output Device
2. BlackHole not in Multi-Output Device
3. Wrong device selected in CallScribe

**Solutions:**
1. Check video app audio settings (Speaker = Multi-Output Device)
2. Recreate Multi-Output Device with BlackHole checked
3. Use `--list-devices` to verify device IDs
4. Test with `--save-audio` to check audio files

### Only hearing remote participants, not myself

**Problem:** Transcript shows only what others said

**Cause:** Microphone stream not captured

**Solutions:**
1. Ensure `--device` points to your microphone (not BlackHole)
2. Verify video app Microphone setting is NOT Multi-Output Device
3. Check CallScribe shows "Microphone device: X" at startup

### Only hearing myself, not remote participants

**Problem:** Transcript shows only what you said

**Cause:** System audio not captured

**Solutions:**
1. Verify video app Speaker/Output set to Multi-Output Device
2. Check Multi-Output Device includes BlackHole
3. Ensure CallScribe detected correct BlackHole device ID

### Audio quality is poor

**Problem:** Transcript has many errors

**Solutions:**
1. Use larger Whisper model: `--model medium` or `--model large`
2. Check microphone positioning and audio levels
3. Reduce background noise
4. Ensure good internet connection (affects remote audio quality)

### Can't hear audio during recording

**Problem:** No audio in speakers while recording

**Cause:** System audio not routed to speakers

**Solutions:**
1. Ensure Multi-Output Device includes your speakers/headphones
2. Check both BlackHole AND speakers are checked in Multi-Output Device
3. Adjust volume in System Preferences → Sound

### Recording hangs or freezes

**Problem:** Recording doesn't stop cleanly

**Solutions:**
1. Use Ctrl+C to force stop
2. Check no other apps are using the audio devices
3. Restart CallScribe and try again

## Best Practices

### Before the Meeting

1. **Test Your Setup:**
   ```bash
   python -m callscribe.main --detect-video-apps
   ```

2. **Do a Test Recording:**
   - Start CallScribe with `--video-conference --save-audio`
   - Join a test call or play a video
   - Record for 30 seconds
   - Check the audio files to verify both streams

3. **Configure Video App:**
   - Set Speaker to Multi-Output Device
   - Keep Microphone as your actual mic
   - Save settings

### During the Meeting

1. **Start CallScribe First** (or early in the meeting)
2. **Verify Detection:**
   - Web GUI: Check for "Video Conference Apps Detected" banner
   - CLI: Review detection report at startup
3. **Monitor Status:**
   - Watch duration counter
   - Check activity log for issues

### After the Meeting

1. **Stop Recording Promptly** after meeting ends
2. **Review Transcript** for accuracy
3. **Save Important Meetings:**
   - Enable "Full Report" for Claude analysis
   - Use `--save-audio` to archive the call

### For Important Meetings

```bash
# High-quality recording with full analysis
python -m callscribe.main \
  --video-conference \
  --model medium \
  --full-report \
  --save-audio \
  --timestamps \
  --output important_meeting.txt
```

## Security & Privacy

### Recording Consent

**⚠️ LEGAL WARNING:** Recording laws vary by jurisdiction.

- **One-party consent** states: Only you need to consent
- **Two-party consent** states: ALL participants must consent
- **Know your local laws** before recording

**Best Practice:** Always announce at the start:
> "This meeting is being recorded and transcribed for [purpose]. Does anyone object?"

### Data Storage

- **Transcripts:** Saved locally in `output/` directory
- **Audio Files:** Stored locally (only with `--save-audio`)
- **Claude API:** Only transcript text sent (not audio)
- **No Cloud Storage:** Everything stays on your machine

### Protecting Recordings

```bash
# Encrypt sensitive recordings
openssl enc -aes-256-cbc -in recording.wav -out recording.wav.enc

# Delete originals after encryption
rm recording.wav

# Decrypt when needed
openssl enc -d -aes-256-cbc -in recording.wav.enc -out recording.wav
```

## Advanced Usage

### Custom Audio Devices

Find device IDs:
```bash
python -m callscribe.main --list-devices
```

Use specific devices:
```bash
python -m callscribe.main \
  --video-conference \
  --device 1 \          # Your microphone
  --system-device 3     # BlackHole
```

### Streaming Mode

For real-time transcription during video calls:

**Web GUI:** Select "Streaming" mode + Enable "Video Conference Mode"

**CLI:**
```bash
# Streaming not yet supported in CLI for video conference mode
# Use Web GUI for streaming video conferences
```

### Multiple Participants

Video conference mode works with any number of participants:
- All remote voices captured through system audio
- Your voice captured through microphone
- Whisper transcribes the combined audio
- For speaker identification, enable "Speaker Detection" (experimental)

## Platform Support

### macOS
✅ **Fully Supported**
- BlackHole for system audio capture
- Multi-Output Device for audio routing

### Linux
⚠️ **Experimental**
- Use PulseAudio or JACK for virtual audio routing
- Alternative to BlackHole: `snd-aloop` module

### Windows
⚠️ **Experimental**
- Use VB-CABLE or Virtual Audio Cable
- Similar concept to BlackHole

## Performance

### CPU Usage
- Dual-stream recording: Minimal overhead
- Transcription: Same as regular recording
- Real-time streaming: Uses 'tiny' model (fast)

### Disk Space
With `--save-audio`, 3 audio files saved:
- Combined: ~10 MB per hour (16kHz, mono)
- Mic only: ~10 MB per hour
- System only: ~10 MB per hour
- **Total: ~30 MB per hour**

### Memory
- Standard mode: ~2 GB RAM (base model)
- Larger models: Up to 10 GB (large model)

## Related Documentation

- **[README.md](README.md)** - Main project overview
- **[WEB_GUI_GUIDE.md](WEB_GUI_GUIDE.md)** - Web interface guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[STREAMING_GUIDE.md](STREAMING_GUIDE.md)** - Streaming mode details

## Support

### Common Questions

**Q: Do I need BlackHole for regular recording?**
A: No, BlackHole is only needed for video conferencing mode.

**Q: Can I use this with phone calls?**
A: Yes, if you route phone call audio through your computer (e.g., via Bluetooth or FaceTime).

**Q: Will participants know I'm recording?**
A: No technical notification, but you must inform them legally and ethically.

**Q: Can I record multiple video calls simultaneously?**
A: No, CallScribe records one session at a time.

**Q: Does this work with screen sharing?**
A: Yes, it captures all audio regardless of screen sharing status.

## Updates

- **v2.0** - Added video conferencing support
  - Dual-stream recording
  - Automatic app detection
  - Web GUI integration
  - CLI support
