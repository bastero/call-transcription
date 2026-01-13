# Real-Time Streaming Transcription Guide

## Overview

Streaming mode allows CallScribe to transcribe audio **as you speak**, providing live feedback during recordings. Instead of waiting until the end, you see transcripts appear every 5 seconds.

## When to Use Streaming Mode

**Best for:**
- Live presentations where you want to see transcripts in real-time
- Long meetings where you want periodic updates
- Interactive sessions where immediate feedback is helpful
- Testing and demos

**Not ideal for:**
- Short recordings (< 1 minute)
- When you need maximum accuracy (use standard mode with larger models)
- Very fast-paced conversations

## Quick Start

### Basic Streaming

```bash
source venv/bin/activate
python -m callscribe.main --streaming
```

### With Timestamps

```bash
python -m callscribe.main --streaming --timestamps
```

### With Full Analysis

```bash
python -m callscribe.main --streaming --full-report
```

## How It Works

1. **Chunk Processing**: Audio is processed in 5-second chunks
2. **Real-Time Transcription**: Each chunk is transcribed immediately
3. **Live Display**: Transcripts appear in your terminal as you speak
4. **Complete Transcript**: Full transcript saved at the end

## Performance

### Model Selection

Streaming mode automatically uses the **'tiny' Whisper model** for speed:

- **Tiny model**: ~2-3x faster than real-time
  - Processes 5 seconds of audio in ~2 seconds
  - Best for real-time feedback

- **Base model**: ~1x real-time
  - Can be used but may lag: `--model base --streaming`
  - Better accuracy, slower feedback

**Larger models (small, medium, large) are NOT recommended for streaming**

### Processing Time

- **5-second chunks**: Typical processing ~2-3 seconds
- **Latency**: ~2-8 seconds from speaking to seeing text
- **Long meetings**: No slowdown, consistent performance

## Usage Examples

### 1. Live Presentation

```bash
# Stream transcription, save everything
python -m callscribe.main --streaming --save-audio --full-report
```

**What happens:**
1. Press ENTER to start
2. Begin presenting
3. See transcripts appear every 5 seconds
4. Press ENTER when done
5. Get complete transcript + Claude analysis

### 2. Quick Voice Note

```bash
# Fast streaming, skip analysis
python -m callscribe.main --streaming --skip-analysis
```

### 3. Interview Recording

```bash
# Streaming with speaker detection
python -m callscribe.main --streaming --diarize --num-speakers 2
```

## Output Display

### During Recording

```
╭──────────────────────────╮
│ 🔴 LIVE - Transcribing   │
│ Speak naturally...       │
│ Press ENTER to stop...   │
╰──────────────────────────╯

[Chunk 1] Hello and welcome to today's meeting.

[Chunk 2] We're going to discuss the quarterly results and plan for next quarter.

[Chunk 3] Let's start with the sales numbers...
```

### After Recording

```
╭──────────────── Complete Transcript ────────────────╮
│ Hello and welcome to today's meeting. We're going   │
│ to discuss the quarterly results and plan for next  │
│ quarter. Let's start with the sales numbers...      │
╰─────────────────────────────────────────────────────╯

✓ Streaming transcription complete!
Processed 12 chunks
Transcript saved to: output/transcript_20260110_153045.txt
```

## Tips for Best Results

### 1. Speak Clearly
- Maintain consistent volume
- Minimize background noise
- Pause briefly between thoughts (helps chunking)

### 2. Monitor the Display
- Watch for transcription errors
- Adjust speaking pace if lagging
- Check chunk numbers to see progress

### 3. Audio Quality
- Use good microphone if available
- Position yourself close to mic
- Reduce echo in the room

### 4. Chunk Timing
- Natural pauses work well with 5-second chunks
- Don't rush - the system keeps up
- Long continuous speech is fine

## Combining with Other Features

### Streaming + Speaker Diarization

```bash
python -m callscribe.main --streaming --diarize --num-speakers 2 --timestamps
```

**Note:** Speaker detection still works but labels are assigned in real-time based on pauses.

### Streaming + Save Audio

```bash
python -m callscribe.main --streaming --save-audio
```

Audio is saved at the end for later reference or reprocessing with better model.

### Streaming + Full Report

```bash
python -m callscribe.main --streaming --full-report --timestamps
```

Complete report with metadata generated after recording ends.

## Troubleshooting

### "Transcription is lagging"

**Solutions:**
- Streaming mode uses 'tiny' model (fastest)
- If still slow, check CPU usage
- Close other applications
- Try shorter chunk duration (requires code modification)

### "Chunks are missing text"

**Possible causes:**
- Silence in those chunks (normal)
- Volume too low
- Background noise drowning out speech

**Fix:**
- Speak louder/closer to mic
- Check microphone settings
- Reduce background noise

### "Text appears jumbled"

This can happen with:
- Very fast speech
- Multiple speakers talking simultaneously
- Poor audio quality

**Fix:**
- Speak one at a time
- Reduce speech pace slightly
- Improve mic quality

### "Model download error"

First run downloads the 'tiny' Whisper model (~75MB).

```bash
# Manually download if needed
python -c "import whisper; whisper.load_model('tiny')"
```

## Comparison: Streaming vs Standard Mode

| Feature | Streaming Mode | Standard Mode |
|---------|---------------|---------------|
| **Live feedback** | ✅ Yes (every 5s) | ❌ No (end only) |
| **Speed** | Fast (tiny model) | Configurable |
| **Accuracy** | Good | Excellent |
| **Best for** | Long meetings | Short recordings |
| **Model** | Tiny (auto) | Any model |
| **Latency** | 2-8 seconds | N/A |

## Advanced Usage

### Custom Chunk Duration

Currently set to 5 seconds. To modify:

Edit `callscribe/main.py`:
```python
streaming_capture = StreamingAudioCapture(
    ...
    chunk_duration=10.0  # Change to 10 seconds
)
```

**Trade-offs:**
- Longer chunks = less frequent updates, better context
- Shorter chunks = more frequent updates, may break sentences

### Force Different Model

```bash
# Use base model (slower but more accurate)
python -m callscribe.main --streaming --model base
```

**Warning:** May not keep up with real-time on slower machines.

## System Requirements

- **CPU**: Modern multi-core processor
- **RAM**: 2GB+ free
- **Disk**: ~100MB for tiny model
- **Network**: None (runs locally)

## Cost

- **Whisper (tiny)**: FREE (local)
- **Claude Analysis**: ~$0.01-0.02/hour (if not skipped)
- **Total**: FREE for transcription, minimal for analysis

## Best Practices

1. **Test First**: Try a 30-second test before important meetings
2. **Monitor Performance**: Watch first few chunks to ensure keeping up
3. **Have Backup**: Save audio with `--save-audio` for reprocessing
4. **Use Timestamps**: `--timestamps` helps track when things were said
5. **Skip Analysis**: Use `--skip-analysis` during recording, analyze later

## Next Steps

- Try streaming mode on a test recording
- Experiment with different scenarios
- Combine with speaker diarization
- Use for live note-taking

Streaming mode makes CallScribe interactive and responsive!
