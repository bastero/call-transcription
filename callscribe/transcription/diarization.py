"""Speaker diarization module using pyannote.audio."""

from typing import Dict, List, Tuple, Optional
import numpy as np
from pathlib import Path
import os


class SpeakerDiarizer:
    """Handles speaker diarization to identify different speakers."""

    def __init__(self, hf_token: Optional[str] = None):
        """
        Initialize speaker diarizer.

        Args:
            hf_token: HuggingFace token for downloading models (required)
        """
        self.hf_token = hf_token or os.getenv("HUGGINGFACE_TOKEN")
        self.pipeline = None

        if not self.hf_token:
            print("⚠️  HuggingFace token not found. Speaker diarization will be disabled.")
            print("   Get a token from: https://huggingface.co/settings/tokens")
            print("   Add to .env: HUGGINGFACE_TOKEN=your_token_here")
            return

    def load_pipeline(self):
        """Load the diarization pipeline."""
        if not self.hf_token:
            return False

        try:
            from pyannote.audio import Pipeline

            if self.pipeline is None:
                print("📥 Loading speaker diarization model...")
                self.pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=self.hf_token
                )
                print("✓ Diarization model loaded")
            return True
        except Exception as e:
            print(f"❌ Error loading diarization model: {e}")
            print("   Make sure you've accepted the model conditions at:")
            print("   https://huggingface.co/pyannote/speaker-diarization-3.1")
            return False

    def diarize_file(self, audio_path: str, num_speakers: Optional[int] = None) -> Dict:
        """
        Perform speaker diarization on an audio file.

        Args:
            audio_path: Path to audio file
            num_speakers: Optional hint for number of speakers

        Returns:
            Dictionary with speaker segments
        """
        if not self.load_pipeline():
            return {"segments": [], "speakers": []}

        print(f"🎯 Analyzing speakers in audio...")

        try:
            # Run diarization
            diarization = self.pipeline(
                audio_path,
                num_speakers=num_speakers
            )

            # Extract segments
            segments = []
            speakers = set()

            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
                speakers.add(speaker)

            result = {
                "segments": segments,
                "speakers": sorted(list(speakers)),
                "num_speakers": len(speakers)
            }

            print(f"✓ Found {len(speakers)} speaker(s)")
            return result

        except Exception as e:
            print(f"❌ Error during diarization: {e}")
            return {"segments": [], "speakers": []}

    def align_with_transcript(
        self,
        diarization_result: Dict,
        transcript_segments: List[Dict]
    ) -> List[Dict]:
        """
        Align speaker labels with transcript segments.

        Args:
            diarization_result: Result from diarize_file
            transcript_segments: Segments from Whisper transcription

        Returns:
            Transcript segments with speaker labels
        """
        if not diarization_result.get("segments"):
            # No diarization available, return original
            return transcript_segments

        aligned_segments = []
        diar_segments = diarization_result["segments"]

        for trans_seg in transcript_segments:
            trans_start = trans_seg["start"]
            trans_end = trans_seg["end"]
            trans_mid = (trans_start + trans_end) / 2

            # Find overlapping speaker segment
            speaker = "Unknown"
            max_overlap = 0

            for diar_seg in diar_segments:
                # Calculate overlap
                overlap_start = max(trans_start, diar_seg["start"])
                overlap_end = min(trans_end, diar_seg["end"])
                overlap = max(0, overlap_end - overlap_start)

                if overlap > max_overlap:
                    max_overlap = overlap
                    speaker = diar_seg["speaker"]

            aligned_segments.append({
                **trans_seg,
                "speaker": speaker
            })

        return aligned_segments

    def format_transcript_with_speakers(
        self,
        aligned_segments: List[Dict],
        include_timestamps: bool = True
    ) -> str:
        """
        Format transcript with speaker labels.

        Args:
            aligned_segments: Segments with speaker labels
            include_timestamps: Whether to include timestamps

        Returns:
            Formatted transcript string
        """
        lines = []
        current_speaker = None

        for segment in aligned_segments:
            speaker = segment.get("speaker", "Unknown")
            text = segment["text"].strip()

            if not text:
                continue

            # Add speaker label if changed
            if speaker != current_speaker:
                if lines:  # Add blank line between speakers
                    lines.append("")
                current_speaker = speaker

            if include_timestamps:
                timestamp = self._format_timestamp(segment["start"])
                lines.append(f"[{timestamp}] {speaker}: {text}")
            else:
                # Group consecutive segments from same speaker
                if lines and lines[-1].startswith(f"{speaker}:"):
                    lines[-1] += f" {text}"
                else:
                    lines.append(f"{speaker}: {text}")

        return "\n".join(lines)

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format seconds as MM:SS timestamp."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def get_speaker_stats(self, aligned_segments: List[Dict]) -> Dict:
        """
        Get statistics about speaker participation.

        Args:
            aligned_segments: Segments with speaker labels

        Returns:
            Dictionary with speaker statistics
        """
        stats = {}

        for segment in aligned_segments:
            speaker = segment.get("speaker", "Unknown")
            duration = segment["end"] - segment["start"]
            word_count = len(segment["text"].split())

            if speaker not in stats:
                stats[speaker] = {
                    "total_time": 0,
                    "segment_count": 0,
                    "word_count": 0
                }

            stats[speaker]["total_time"] += duration
            stats[speaker]["segment_count"] += 1
            stats[speaker]["word_count"] += word_count

        return stats


def test_diarization():
    """Test speaker diarization."""
    print("Speaker diarization module loaded")
    print("Requires HuggingFace token to use")


if __name__ == "__main__":
    test_diarization()
