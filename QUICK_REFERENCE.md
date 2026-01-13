# CallScribe Quick Reference

## Launch Commands

### Web GUI (Recommended)
```bash
python -m callscribe gui
```
Opens browser to http://localhost:5000

### CLI - Standard Recording
```bash
python -m callscribe.main
```

### CLI - Streaming (Real-time)
```bash
python -m callscribe.main --streaming
```

### CLI - Pausable (Interactive)
```bash
python -m callscribe.main --pausable
```

## Common Options

```bash
# Speaker diarization (2 speakers)
--diarize --num-speakers 2

# Include timestamps
--timestamps

# Save audio file
--save-audio

# Full Claude analysis
--full-report

# Skip Claude analysis
--skip-analysis

# Choose Whisper model
--model tiny|base|small|medium|large

# List audio devices
--list-devices

# Use specific device
--device 2
```

## Example Commands

### Quick Meeting Transcript
```bash
python -m callscribe.main --timestamps
```

### Meeting with Speakers
```bash
python -m callscribe.main --diarize --num-speakers 3 --timestamps --full-report
```

### Live Monitoring
```bash
python -m callscribe.main --streaming --timestamps
```

### Long Session with Breaks
```bash
python -m callscribe.main --pausable --save-audio --full-report
```

### Full Featured
```bash
python -m callscribe.main \
  --pausable \
  --diarize \
  --num-speakers 2 \
  --timestamps \
  --full-report \
  --save-audio \
  --model base
```

## Web GUI Quick Start

1. Launch server:
   ```bash
   python -m callscribe gui
   ```

2. Desktop: Browser opens automatically

3. Mobile: Scan QR code shown in interface

4. Select mode: Standard / Streaming / Pausable

5. Configure options (checkboxes)

6. Click "Start Recording"

7. Control from any connected device

## Pausable Mode Controls (CLI)

During recording, type:
- `p` + ENTER = Pause
- `r` + ENTER = Resume
- `s` + ENTER = Stop
- `status` = Show current status

## Recording Modes Comparison

| Mode | Best For | Live Updates |
|------|----------|--------------|
| **Standard** | Short recordings | No |
| **Streaming** | Long meetings | Yes (5s) |
| **Pausable** | Sessions with breaks | No |

## Output Files

All files saved to `output/` directory:

- `transcript_YYYYMMDD_HHMMSS.txt` - Transcript
- `analysis_YYYYMMDD_HHMMSS.md` - Claude analysis (if enabled)
- `metadata_YYYYMMDD_HHMMSS.json` - Recording metadata
- `audio_YYYYMMDD_HHMMSS.wav` - Audio file (if --save-audio)

## Whisper Model Selection

| Model | Speed | Accuracy | RAM |
|-------|-------|----------|-----|
| tiny | Fastest | Good | 1GB |
| base | Fast | Better | 1GB |
| small | Medium | Great | 2GB |
| medium | Slow | Excellent | 5GB |
| large | Slowest | Best | 10GB |

**Recommendation:** Use `base` for balanced speed/quality

## Cost

- Whisper: **FREE** (local)
- Speaker Diarization: **FREE** (pause-based)
- Web GUI: **FREE** (local)
- Claude Analysis: **~$0.01-0.02/hour** (optional, can skip)

## Troubleshooting Quick Fixes

**No audio recorded:**
```bash
python -m callscribe.main --list-devices
python -m callscribe.main --device [number]
```

**Web GUI won't start:**
```bash
# Try different port
python -m callscribe gui --port 8080
```

**Mobile can't connect:**
- Ensure same WiFi network
- Check firewall settings
- Use IP address shown in terminal

**Transcription too slow:**
```bash
# Use faster model
python -m callscribe.main --model tiny
```

**Out of memory:**
```bash
# Use smaller model
python -m callscribe.main --model tiny
```

## Network Access

**Local only:**
```bash
python -m callscribe gui --host localhost
```

**Network access (default):**
```bash
python -m callscribe gui --host 0.0.0.0
```

**Custom port:**
```bash
python -m callscribe gui --port 8080
```

## Documentation Links

- [WEB_GUI_GUIDE.md](WEB_GUI_GUIDE.md) - Complete web GUI guide
- [STREAMING_GUIDE.md](STREAMING_GUIDE.md) - Streaming mode
- [PAUSABLE_GUIDE.md](PAUSABLE_GUIDE.md) - Pausable recording
- [SPEAKER_DIARIZATION_GUIDE.md](SPEAKER_DIARIZATION_GUIDE.md) - Speaker detection
- [SETUP.md](SETUP.md) - Installation guide
- [QUICKSTART.md](QUICKSTART.md) - Getting started

## Environment Variables

Edit `.env` file:
```bash
ANTHROPIC_API_KEY=your_key_here
WHISPER_MODEL=base
SAMPLE_RATE=16000
CHANNELS=1
```

## Support

- Check documentation files for detailed help
- Run with `--help` for CLI options
- Check `output/` directory for generated files
- Review system logs in web GUI

## Tips

1. **Test first** - Try 30-second recording before important meeting
2. **Save audio** - Use `--save-audio` for backup/reprocessing
3. **Choose right mode** - Standard for quick, Streaming for long, Pausable for breaks
4. **Model selection** - Tiny for speed, Base for balance, Large for quality
5. **Mobile monitoring** - Launch web GUI for remote control
6. **Speaker count** - Set correct number for better diarization
7. **Check devices** - Use `--list-devices` to find correct microphone

## One-Liner Examples

```bash
# Quick transcript with speakers
python -m callscribe.main --diarize --num-speakers 2 --timestamps

# Live transcription
python -m callscribe.main --streaming

# Meeting with breaks
python -m callscribe.main --pausable --full-report

# Visual interface
python -m callscribe gui
```

---

**For complete documentation, see README.md and individual guide files.**
