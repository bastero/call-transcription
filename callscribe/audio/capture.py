"""Audio capture module for recording system audio."""

import sounddevice as sd
import numpy as np
import wave
from datetime import datetime
from typing import Optional
import os


class AudioCapture:
    """Handles audio recording from system audio or microphone."""

    def __init__(self, sample_rate: int = 16000, channels: int = 1, device: Optional[int] = None):
        """
        Initialize audio capture.

        Args:
            sample_rate: Sample rate in Hz (16000 recommended for Whisper)
            channels: Number of audio channels (1 for mono, 2 for stereo)
            device: Audio device index (None for default)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device
        self.audio_data = []
        self.is_recording = False

    def list_devices(self):
        """List all available audio devices."""
        print("\n=== Available Audio Devices ===")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            print(f"{i}: {device['name']} (in: {device['max_input_channels']}, out: {device['max_output_channels']})")
        return devices

    def _audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream."""
        if status:
            print(f"Audio status: {status}")
        if self.is_recording:
            self.audio_data.append(indata.copy())

    def start_recording(self):
        """Start recording audio."""
        self.audio_data = []
        self.is_recording = True

        self.stream = sd.InputStream(
            device=self.device,
            channels=self.channels,
            samplerate=self.sample_rate,
            callback=self._audio_callback
        )
        self.stream.start()
        print(f"🎤 Recording started (Device: {self.device or 'default'})")

    def stop_recording(self) -> np.ndarray:
        """
        Stop recording and return audio data.

        Returns:
            NumPy array containing recorded audio
        """
        self.is_recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()

        if not self.audio_data:
            print("⚠️  No audio data recorded")
            return np.array([])

        audio = np.concatenate(self.audio_data, axis=0)
        print(f"✓ Recording stopped ({len(audio)/self.sample_rate:.2f} seconds)")
        return audio

    def save_audio(self, audio_data: np.ndarray, filename: Optional[str] = None) -> str:
        """
        Save audio data to WAV file.

        Args:
            audio_data: NumPy array containing audio
            filename: Output filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"

        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        filepath = os.path.join("output", filename)

        # Normalize audio to 16-bit PCM
        audio_normalized = np.int16(audio_data * 32767)

        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_normalized.tobytes())

        print(f"💾 Audio saved to: {filepath}")
        return filepath


def test_audio_devices():
    """Test function to list and verify audio devices."""
    capture = AudioCapture()
    capture.list_devices()


if __name__ == "__main__":
    test_audio_devices()
