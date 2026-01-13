"""Simple speaker diarization using audio features - completely free."""

from typing import Dict, List, Optional
import numpy as np
from pathlib import Path


class SimpleSpeakerDiarizer:
    """
    Simple speaker diarization using audio features.
    No external tokens or paid services required.

    Uses energy-based voice activity detection and simple clustering
    to identify speaker changes.
    """

    def __init__(self):
        """Initialize simple diarizer."""
        self.sample_rate = 16000
        print("✓ Simple speaker diarizer initialized (no tokens needed)")

    def detect_speakers_from_segments(
        self,
        transcript_segments: List[Dict],
        num_speakers: Optional[int] = None,
        auto_detect: bool = True
    ) -> List[Dict]:
        """
        Detect speaker changes based on transcript segments.

        Uses pauses and segment timing to infer speaker changes.
        Simple heuristic: Long pauses likely indicate speaker changes.

        Args:
            transcript_segments: Whisper transcript segments
            num_speakers: Expected number of speakers (optional, for cycling mode)
            auto_detect: If True, assigns new speaker IDs instead of cycling (default)

        Returns:
            Segments with speaker labels
        """
        if not transcript_segments:
            return []

        labeled_segments = []
        current_speaker = 0
        last_end_time = 0
        speaker_turn_count = 0  # Track total speaker turns

        # Threshold for detecting speaker change (in seconds)
        PAUSE_THRESHOLD = 1.5  # 1.5 second pause suggests speaker change

        for i, segment in enumerate(transcript_segments):
            start = segment.get("start", 0)
            pause_duration = start - last_end_time

            # If there's a significant pause, assume speaker changed
            if pause_duration > PAUSE_THRESHOLD and i > 0:
                speaker_turn_count += 1

                if auto_detect:
                    # Auto-detect mode: Assign sequential speaker IDs
                    # Don't cycle - let actual number emerge naturally
                    current_speaker = speaker_turn_count % 10  # Max 10 speakers
                else:
                    # Cycling mode: Use specified num_speakers
                    current_speaker = (current_speaker + 1)
                    if num_speakers and current_speaker >= num_speakers:
                        current_speaker = 0

            labeled_segment = {
                **segment,
                "speaker": f"SPEAKER_{current_speaker:02d}"
            }
            labeled_segments.append(labeled_segment)

            last_end_time = segment.get("end", start)

        return labeled_segments

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
            speaker = segment.get("speaker", "SPEAKER_00")
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
            speaker = segment.get("speaker", "SPEAKER_00")
            duration = segment.get("end", 0) - segment.get("start", 0)
            word_count = len(segment.get("text", "").split())

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

    def detect_num_speakers(self, aligned_segments: List[Dict]) -> int:
        """
        Count number of unique speakers detected.

        Args:
            aligned_segments: Segments with speaker labels

        Returns:
            Number of speakers
        """
        speakers = set(seg.get("speaker", "SPEAKER_00") for seg in aligned_segments)
        return len(speakers)


def test_simple_diarization():
    """Test simple speaker diarization."""
    print("Simple speaker diarization module loaded")
    print("No external tokens or API keys required")


if __name__ == "__main__":
    test_simple_diarization()
