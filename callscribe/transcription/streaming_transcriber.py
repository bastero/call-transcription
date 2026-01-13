"""Streaming transcription for real-time audio processing."""

import whisper
import numpy as np
from typing import Dict, List, Optional, Callable
import threading
import queue
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text


class StreamingTranscriber:
    """Handles real-time streaming transcription."""

    def __init__(self, model_name: str = "tiny", device: str = "cpu"):
        """
        Initialize streaming transcriber.

        Args:
            model_name: Whisper model (recommend 'tiny' or 'base' for real-time)
            device: Device to run on ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.transcripts = []
        self.console = Console()

        if model_name not in ["tiny", "base"]:
            print(f"⚠️  Warning: '{model_name}' may be too slow for real-time.")
            print("   Recommend using 'tiny' or 'base' for streaming.")

        print(f"📥 Loading Whisper '{model_name}' for streaming...")

    def load_model(self):
        """Load the Whisper model."""
        if self.model is None:
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"✓ Whisper '{self.model_name}' loaded for streaming")

    def transcribe_chunk(
        self,
        audio_chunk: np.ndarray,
        sample_rate: int = 16000,
        language: str = "en"
    ) -> Dict:
        """
        Transcribe a single audio chunk.

        Args:
            audio_chunk: Audio data as NumPy array
            sample_rate: Sample rate of audio
            language: Language code

        Returns:
            Transcription result
        """
        if self.model is None:
            self.load_model()

        # Ensure audio is float32 and normalized
        if audio_chunk.dtype != np.float32:
            audio_chunk = audio_chunk.astype(np.float32)

        # Flatten if stereo
        if len(audio_chunk.shape) > 1:
            audio_chunk = audio_chunk.mean(axis=1)

        # Normalize
        if audio_chunk.max() > 1.0 or audio_chunk.min() < -1.0:
            audio_chunk = audio_chunk / np.abs(audio_chunk).max()

        # Transcribe
        result = self.model.transcribe(
            audio_chunk,
            language=language,
            verbose=False,
            temperature=0.0,
            fp16=False
        )

        return result

    def stream_transcribe(
        self,
        audio_chunk: np.ndarray,
        chunk_number: int,
        sample_rate: int = 16000
    ) -> str:
        """
        Transcribe chunk and return formatted text.

        Args:
            audio_chunk: Audio chunk to transcribe
            chunk_number: Chunk number (for tracking)
            sample_rate: Sample rate

        Returns:
            Transcribed text
        """
        # Skip if chunk is too short or silent
        if len(audio_chunk) < sample_rate * 0.5:  # Less than 0.5 seconds
            return ""

        # Check if chunk is mostly silence
        if np.abs(audio_chunk).max() < 0.01:
            return ""

        result = self.transcribe_chunk(audio_chunk, sample_rate)
        text = result.get("text", "").strip()

        if text:
            self.transcripts.append({
                "chunk": chunk_number,
                "text": text,
                "segments": result.get("segments", [])
            })

        return text

    def get_full_transcript(self) -> str:
        """
        Get the complete transcript from all chunks.

        Returns:
            Combined transcript
        """
        return " ".join([t["text"] for t in self.transcripts if t["text"]])

    def get_all_segments(self) -> List[Dict]:
        """
        Get all transcript segments.

        Returns:
            List of all segments
        """
        all_segments = []
        for transcript in self.transcripts:
            all_segments.extend(transcript.get("segments", []))
        return all_segments

    def clear_transcripts(self):
        """Clear all stored transcripts."""
        self.transcripts = []


class LiveTranscriptDisplay:
    """Display live transcript updates in the terminal."""

    def __init__(self):
        """Initialize live display."""
        self.transcript_lines = []
        self.console = Console()

    def update(self, new_text: str, chunk_number: int):
        """
        Update the display with new transcribed text.

        Args:
            new_text: New transcribed text
            chunk_number: Chunk number
        """
        if new_text:
            self.transcript_lines.append(f"[Chunk {chunk_number}] {new_text}")

    def get_display_text(self) -> Text:
        """Get formatted text for display."""
        text = Text()
        for line in self.transcript_lines[-10:]:  # Show last 10 chunks
            text.append(line + "\n")
        return text

    def clear(self):
        """Clear the display."""
        self.transcript_lines = []


def create_streaming_callback(
    transcriber: StreamingTranscriber,
    display: Optional[LiveTranscriptDisplay] = None,
    chunk_counter: List[int] = None
):
    """
    Create a callback function for streaming audio processing.

    Args:
        transcriber: StreamingTranscriber instance
        display: Optional live display
        chunk_counter: List to track chunk count

    Returns:
        Callback function
    """
    if chunk_counter is None:
        chunk_counter = [0]

    def callback(audio_chunk: np.ndarray):
        """Process audio chunk."""
        chunk_counter[0] += 1
        text = transcriber.stream_transcribe(audio_chunk, chunk_counter[0])

        if text and display:
            display.update(text, chunk_counter[0])
            # Print to console
            print(f"\n[Chunk {chunk_counter[0]}] {text}")

    return callback
