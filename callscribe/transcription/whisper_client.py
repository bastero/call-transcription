"""Whisper transcription module using local OpenAI Whisper."""

import whisper
import numpy as np
from typing import Dict, Optional
import os


class WhisperTranscriber:
    """Handles audio transcription using local Whisper model."""

    def __init__(self, model_name: str = "base", device: str = "cpu"):
        """
        Initialize Whisper transcriber.

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        print(f"📥 Loading Whisper model '{model_name}'...")

    def load_model(self):
        """Load the Whisper model."""
        if self.model is None:
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"✓ Whisper model '{self.model_name}' loaded")

    def transcribe_file(self, audio_path: str, language: Optional[str] = "en") -> Dict:
        """
        Transcribe an audio file.

        Args:
            audio_path: Path to audio file
            language: Language code (en, es, fr, etc.) or None for auto-detect

        Returns:
            Dictionary containing transcript and metadata
        """
        if self.model is None:
            self.load_model()

        print(f"🎯 Transcribing audio file: {audio_path}")
        if language:
            print(f"   Language: {language}")
        else:
            print(f"   Language: Auto-detect")

        result = self.model.transcribe(
            audio_path,
            language=language,
            verbose=False,
            temperature=0.0,
            fp16=False  # Set to True if using CUDA
        )

        detected_lang = result.get('language', 'unknown')
        print(f"✓ Transcription complete (language: {detected_lang})")
        return result

    def transcribe_array(self, audio_data: np.ndarray, sample_rate: int = 16000, language: Optional[str] = "en") -> Dict:
        """
        Transcribe audio from NumPy array.

        Args:
            audio_data: Audio data as NumPy array
            sample_rate: Sample rate of audio
            language: Language code or None for auto-detect

        Returns:
            Dictionary containing transcript and metadata
        """
        if self.model is None:
            self.load_model()

        # Ensure audio is float32 and normalized
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Flatten if stereo
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)

        # Normalize to [-1, 1]
        if audio_data.max() > 1.0 or audio_data.min() < -1.0:
            audio_data = audio_data / np.abs(audio_data).max()

        print(f"🎯 Transcribing audio ({len(audio_data)/sample_rate:.2f} seconds)")
        if language:
            print(f"   Language: {language}")
        else:
            print(f"   Language: Auto-detect")

        result = self.model.transcribe(
            audio_data,
            language=language,
            verbose=False,
            temperature=0.0,
            fp16=False
        )

        detected_lang = result.get('language', 'unknown')
        print(f"✓ Transcription complete (language: {detected_lang})")
        return result

    def format_transcript(self, result: Dict, include_timestamps: bool = True) -> str:
        """
        Format transcription result as readable text.

        Args:
            result: Transcription result from Whisper
            include_timestamps: Whether to include timestamps

        Returns:
            Formatted transcript string
        """
        if include_timestamps and 'segments' in result:
            lines = []
            for segment in result['segments']:
                timestamp = self._format_timestamp(segment['start'])
                text = segment['text'].strip()
                lines.append(f"[{timestamp}] {text}")
            return "\n".join(lines)
        else:
            return result['text'].strip()

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format seconds as MM:SS timestamp."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"


def test_whisper():
    """Test Whisper transcription."""
    transcriber = WhisperTranscriber(model_name="base")
    print("Whisper transcriber initialized successfully")


if __name__ == "__main__":
    test_whisper()
