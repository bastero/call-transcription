# Speaker Diarization Guide

## Overview

Speaker diarization allows CallScribe to identify and label different speakers in your recordings. This is particularly useful for:
- Multi-person meetings
- Interviews
- Panel discussions
- Conference calls

## Setup

### 1. Get a HuggingFace Token

Speaker diarization requires a free HuggingFace account and token:

1. Create an account at https://huggingface.co/join
2. Go to https://huggingface.co/settings/tokens
3. Create a new token (read access is sufficient)
4. Accept the model conditions at https://huggingface.co/pyannote/speaker-diarization-3.1

### 2. Add Token to .env

Edit your `.env` file:

```bash
nano .env
```

Add the following line:

```
HUGGINGFACE_TOKEN=hf_your_token_here
```

Save and exit (Ctrl+X, Y, Enter)

### 3. Verify Installation

```bash
source venv/bin/activate
python -c "from callscribe.transcription.diarization import SpeakerDiarizer; print('✓ Diarization ready')"
```

## Usage

### Basic Speaker Diarization

```bash
# Enable speaker diarization with --diarize flag
python -m callscribe.main --diarize --timestamps
```

### With Known Number of Speakers

If you know how many speakers are in the conversation, provide a hint for better accuracy:

```bash
# For a 2-person conversation
python -m callscribe.main --diarize --num-speakers 2 --timestamps

# For a 4-person meeting
python -m callscribe.main --diarize --num-speakers 4 --timestamps
```

### Full Analysis with Speaker Identification

```bash
python -m callscribe.main --diarize --timestamps --full-report
```

## Output Format

### Without Diarization
```
[00:05] Testing testing testing. Can you hear me?
[00:12] Yes, I can hear you clearly.
```

### With Diarization
```
[00:05] SPEAKER_00: Testing testing testing. Can you hear me?

[00:12] SPEAKER_01: Yes, I can hear you clearly.
```

## Speaker Statistics

When diarization is enabled, CallScribe shows participation statistics:

```
✓ Identified 3 speaker(s)
  SPEAKER_00: 45.2s, 124 words
  SPEAKER_01: 38.7s, 98 words
  SPEAKER_02: 22.1s, 56 words
```

## Performance Notes

- **First Run**: Downloads the diarization model (~1.2GB) - may take several minutes
- **Processing Time**: Adds 2-5x the audio duration
  - 1 minute audio = 2-5 minutes processing
  - 10 minute meeting = 20-50 minutes total
- **Accuracy**: Best with:
  - Clear audio
  - Distinct voices
  - Minimal background noise
  - 2-6 speakers (accuracy decreases with more speakers)

## Tips for Best Results

1. **Use Good Audio Quality**
   - Use external microphone if possible
   - Minimize background noise
   - Ensure all speakers are audible

2. **Provide Speaker Count**
   - If you know the number, use `--num-speakers X`
   - This significantly improves accuracy

3. **Shorter Segments**
   - Process meetings in 10-15 minute chunks
   - Combine transcripts afterward if needed

## Troubleshooting

### "HuggingFace token not found"

Make sure:
- `.env` file exists in project root
- `HUGGINGFACE_TOKEN` is set correctly
- No extra spaces or quotes around the token

### "Model conditions not accepted"

Visit https://huggingface.co/pyannote/speaker-diarization-3.1 and accept the terms of use.

### Slow Processing

- Use smaller Whisper model: `--model tiny`
- Process shorter segments
- Expect 2-5x real-time processing

### Poor Speaker Separation

- Check audio quality
- Provide `--num-speakers` hint
- Ensure speakers have distinct voices
- Reduce background noise

## Example Workflows

### Interview Recording
```bash
# 2 speakers, full analysis
python -m callscribe.main --diarize --num-speakers 2 --timestamps --full-report
```

### Team Meeting (4 people)
```bash
# 4 speakers, save audio, full report
python -m callscribe.main --diarize --num-speakers 4 --timestamps --save-audio --full-report
```

### Panel Discussion (unknown speakers)
```bash
# Auto-detect speakers
python -m callscribe.main --diarize --timestamps --full-report
```

## Cost

- **HuggingFace Token**: FREE
- **Diarization Model**: FREE (runs locally)
- **Processing**: Uses your CPU (no cloud costs)
- **Claude Analysis**: Same as before (~$0.01-0.02/hour)

## Next Steps

Once you have speaker diarization working:
- Try different meeting types
- Experiment with the `--num-speakers` parameter
- Use with Google Meet recordings (after BlackHole setup)

## Technical Details

CallScribe uses:
- **pyannote.audio 3.1**: State-of-the-art speaker diarization
- **Alignment Algorithm**: Matches speaker segments with Whisper transcription
- **Statistics Tracking**: Analyzes speaking time and word count per speaker
