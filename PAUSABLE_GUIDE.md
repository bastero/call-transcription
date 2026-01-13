# Pausable Recording Guide

## Overview

Pausable mode allows you to **pause and resume** your recording session interactively. Perfect for recordings with natural breaks, multiple sessions, or when you need control over what gets captured.

## When to Use Pausable Mode

**Best for:**
- Meetings with breaks or intermissions
- Recording multiple separate segments in one session
- Presentations where you need to pause between sections
- Situations where you want to exclude certain parts from the recording
- Long sessions where you need flexibility to stop and continue

**Not ideal for:**
- Continuous recordings without breaks
- Quick voice notes (use standard mode)
- Real-time feedback needs (use streaming mode)

## Quick Start

### Basic Pausable Recording

```bash
source venv/bin/activate
python -m callscribe.main --pausable
```

### With Speaker Diarization

```bash
python -m callscribe.main --pausable --diarize --num-speakers 2
```

### With Timestamps and Full Report

```bash
python -m callscribe.main --pausable --timestamps --full-report
```

### Save Audio for Later Reprocessing

```bash
python -m callscribe.main --pausable --save-audio
```

## How It Works

1. **Start Recording**: Press ENTER to begin capturing audio
2. **Pause Anytime**: Type 'p' and press ENTER to pause
3. **Resume**: Type 'r' and press ENTER to continue recording
4. **Check Status**: Type 'status' to see current state and segment count
5. **Stop**: Type 's' and press ENTER when finished
6. **Complete Transcript**: All segments are combined and transcribed

## Interactive Controls

### During Recording

```
╭──────────────────────────────────────╮
│ 🎙️  PAUSABLE RECORDING CONTROLS      │
│                                       │
│ 'p' + ENTER  →  Pause recording      │
│ 'r' + ENTER  →  Resume recording     │
│ 's' + ENTER  →  Stop & finish        │
│ 'status'     →  Show current status  │
╰──────────────────────────────────────╯
```

### Control Details

- **Pause ('p')**:
  - Immediately stops capturing audio
  - Saves current segment to memory
  - Microphone remains active but audio is not recorded
  - Display shows "⏸️  PAUSED"

- **Resume ('r')**:
  - Starts capturing audio again
  - Creates a new audio segment
  - Display shows "🔴 RECORDING"

- **Status ('status')**:
  - Shows current state (Recording/Paused)
  - Displays number of segments captured
  - Shows total recording duration
  - Microphone stays in current state

- **Stop ('s')**:
  - Ends the recording session
  - Combines all segments
  - Proceeds to transcription

## Usage Examples

### 1. Meeting with Breaks

```bash
python -m callscribe.main --pausable --diarize --num-speakers 3 --full-report
```

**Workflow:**
1. Press ENTER to start
2. Record opening discussion
3. Type 'p' during coffee break
4. Type 'r' when meeting resumes
5. Type 'p' during lunch break
6. Type 'r' for afternoon session
7. Type 's' when meeting ends

**Result:** One complete transcript excluding break times, with speaker labels and full analysis.

### 2. Multi-Part Presentation

```bash
python -m callscribe.main --pausable --timestamps --save-audio
```

**Workflow:**
1. Record introduction
2. Pause during slide transitions
3. Resume for each section
4. Check 'status' to track progress
5. Stop after conclusion

**Result:** Segmented transcript with timestamps, audio saved for reference.

### 3. Interview Recording

```bash
python -m callscribe.main --pausable --diarize --num-speakers 2 --timestamps
```

**Workflow:**
1. Start interview
2. Pause during technical issues
3. Resume when ready
4. Pause to check questions
5. Resume for next topic
6. Stop at end

**Result:** Clean transcript with speaker labels, excluding paused segments.

## Output Display

### During Active Recording

```
╭──────────────────────────────────────╮
│ 🔴 RECORDING                         │
│ Segment: 2                           │
│ Total Duration: 3m 45s               │
│                                      │
│ Type command: _                      │
╰──────────────────────────────────────╯
```

### During Pause

```
╭──────────────────────────────────────╮
│ ⏸️  PAUSED                            │
│ Segments: 3                          │
│ Duration: 5m 12s                     │
│                                      │
│ Type 'r' to resume: _                │
╰──────────────────────────────────────╯
```

### After Recording

```
✓ Recording stopped
  3 segments captured
  Total duration: 8m 27s

🎯 Transcribing audio...
✓ Transcription complete (387 words)

🎯 Analyzing transcript...
✓ Analysis complete

╭──────────────── Complete Transcript ────────────────╮
│ [Combined transcript from all segments]              │
╰──────────────────────────────────────────────────────╯

Files saved:
  • transcript_20260110_153045.txt
  • analysis_20260110_153045.txt
  • metadata_20260110_153045.json
```

## Tips for Best Results

### 1. Plan Your Segments
- Think about natural break points before recording
- Pause during transitions, not mid-sentence
- Use pauses to exclude irrelevant content

### 2. Monitor Segment Count
- Use 'status' command to track how many segments you have
- Too many short segments may affect transcription quality
- Aim for meaningful segment lengths (> 30 seconds)

### 3. Audio Continuity
- Segments are combined seamlessly
- Transcription treats combined audio as continuous
- Speaker detection works across segments

### 4. Quick Commands
- Commands take effect immediately
- No need to wait between pause/resume
- 'status' doesn't interrupt recording state

## Combining with Other Features

### Pausable + Speaker Diarization

```bash
python -m callscribe.main --pausable --diarize --num-speakers 2
```

Speaker detection works across all segments, identifying speakers throughout pauses.

### Pausable + Save Audio

```bash
python -m callscribe.main --pausable --save-audio
```

Combined audio from all segments is saved. Can be reprocessed later with different settings.

### Pausable + Full Report

```bash
python -m callscribe.main --pausable --full-report --timestamps
```

Complete analysis including:
- Number of segments (pause count)
- Total active recording time
- Combined transcript
- Claude analysis
- Metadata with segment information

## Metadata Output

Pausable recordings include special metadata:

```json
{
  "recording_mode": "pausable",
  "segments_captured": 3,
  "total_duration": "8m 27s",
  "pause_count": 2,
  "segment_durations": ["2m 15s", "3m 30s", "2m 42s"],
  "timestamp": "2026-01-10 15:30:45"
}
```

## Troubleshooting

### "Commands not responding"

**Possible causes:**
- Need to press ENTER after typing command
- Terminal not in focus
- Command misspelled

**Fix:**
- Always type command + ENTER
- Click on terminal window
- Use exact commands: 'p', 'r', 's', 'status'

### "Segments not combining properly"

**Possible causes:**
- Audio format inconsistency
- Very short segments (< 0.5s)

**Fix:**
- Keep segments > 1 second
- Avoid rapid pause/resume cycles
- Use standard mode for continuous recording

### "Transcription quality issues"

**Possible causes:**
- Too many very short segments
- Pauses in middle of sentences
- Different audio levels across segments

**Fix:**
- Pause during natural breaks
- Maintain consistent microphone distance
- Aim for longer, meaningful segments
- Use better Whisper model: `--model small`

### "Lost track of current state"

**Solution:**
```bash
# Type this during recording:
status
```

Shows:
- Current state (Recording/Paused)
- Number of segments
- Total duration

## Comparison: Pausable vs Other Modes

| Feature | Pausable Mode | Standard Mode | Streaming Mode |
|---------|--------------|---------------|----------------|
| **Control** | ✅ Full (pause/resume) | ⏹️ Start/stop only | ⏹️ Start/stop only |
| **Segments** | ✅ Multiple | ❌ Single | ❌ Single |
| **Live feedback** | ❌ No (end only) | ❌ No (end only) | ✅ Yes (every 5s) |
| **Flexibility** | ✅ High | ❌ Low | ❌ Low |
| **Best for** | Broken sessions | Quick recordings | Live monitoring |
| **Complexity** | Medium | Low | Medium |

## Advanced Usage

### Custom Segment Management

Currently segments are managed automatically. Future versions may allow:
- Named segments
- Segment-by-segment transcription
- Selective segment deletion

### Combining Multiple Sessions

Each pausable recording creates one combined file. To merge multiple sessions:

```bash
# Session 1
python -m callscribe.main --pausable --save-audio
# Saves: audio_session1.wav, transcript_session1.txt

# Session 2
python -m callscribe.main --pausable --save-audio
# Saves: audio_session2.wav, transcript_session2.txt

# Manually combine files if needed
```

### Processing Specific Segments

For segment-specific analysis, use `--save-audio` and reprocess:

```bash
# Record with segments
python -m callscribe.main --pausable --save-audio

# Later: reprocess with different model
python -m callscribe.main --model large --audio-file saved_audio.wav
```

## System Requirements

- **CPU**: Modern multi-core processor
- **RAM**: 2GB+ free
- **Disk**: Space for temporary segment storage
- **Terminal**: Interactive terminal that accepts input

## Cost

- **Whisper**: FREE (local transcription)
- **Claude Analysis**: ~$0.01-0.02/hour (if not skipped)
- **Speaker Diarization**: FREE (pause-based detection)
- **Total**: FREE for transcription, minimal for analysis

## Best Practices

1. **Test Controls**: Try a 30-second test before important recordings
2. **Plan Pauses**: Identify natural break points beforehand
3. **Use Status**: Check 'status' periodically to track progress
4. **Meaningful Segments**: Avoid very short segments (< 5 seconds)
5. **Save Audio**: Use `--save-audio` for backup and reprocessing
6. **Check Display**: Watch for "RECORDING" vs "PAUSED" indicators

## Workflow Recommendations

### For Long Meetings
```bash
python -m callscribe.main --pausable --diarize --full-report --save-audio
```
- Pause during breaks
- Resume for each session
- Get complete analysis at end
- Audio backup available

### For Presentations
```bash
python -m callscribe.main --pausable --timestamps --skip-analysis
```
- Pause between slides
- Resume for each section
- Quick transcript with timing
- Skip analysis for speed

### For Interviews
```bash
python -m callscribe.main --pausable --diarize --num-speakers 2 --timestamps
```
- Pause during setup issues
- Resume when ready
- Speaker labels maintained
- Timestamps for reference

## Next Steps

- Try pausable mode on a test recording
- Practice using 'p', 'r', 's' commands
- Experiment with different segment lengths
- Combine with diarization for multi-speaker sessions
- Use 'status' command to monitor progress

Pausable mode gives you complete control over your recording sessions!
