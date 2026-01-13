"""Streaming audio capture for real-time transcription."""

import sounddevice as sd
import numpy as np
import queue
import threading
from typing import Optional, Callable
from datetime import datetime


class StreamingAudioCapture:
    """Handles real-time streaming audio capture with chunked processing."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        device: Optional[int] = None,
        chunk_duration: float = 5.0  # Process every 5 seconds
    ):
        """
        Initialize streaming audio capture.

        Args:
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            device: Audio device index
            chunk_duration: Duration of each audio chunk in seconds
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)

        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.stream = None
        self.all_audio = []
        self.callback_function = None

    def _audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream."""
        if status:
            print(f"Audio status: {status}")
        if self.is_recording:
            self.audio_queue.put(indata.copy())
            self.all_audio.append(indata.copy())

    def _process_chunks(self):
        """Process audio chunks in a separate thread."""
        buffer = np.array([]).reshape(0, self.channels)

        while self.is_recording:
            try:
                # Get audio from queue with timeout
                chunk = self.audio_queue.get(timeout=0.5)

                # Check for sentinel value (None means stop)
                if chunk is None:
                    break

                buffer = np.vstack([buffer, chunk])

                # When buffer reaches chunk_size, process it
                if len(buffer) >= self.chunk_size:
                    audio_chunk = buffer[:self.chunk_size]
                    buffer = buffer[self.chunk_size:]

                    # Call the callback function if set and still recording
                    if self.callback_function and self.is_recording:
                        try:
                            self.callback_function(audio_chunk)
                        except Exception as e:
                            print(f"Error in streaming callback: {e}")

            except queue.Empty:
                continue

        # Process remaining buffer
        if len(buffer) > 0 and self.callback_function:
            self.callback_function(buffer)

    def start_streaming(self, callback: Callable[[np.ndarray], None]):
        """
        Start streaming audio with real-time processing.

        Args:
            callback: Function to call with each audio chunk
        """
        self.callback_function = callback
        self.audio_queue = queue.Queue()
        self.all_audio = []
        self.is_recording = True

        # Start audio stream
        self.stream = sd.InputStream(
            device=self.device,
            channels=self.channels,
            samplerate=self.sample_rate,
            callback=self._audio_callback
        )
        self.stream.start()

        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_chunks, daemon=True)
        self.processing_thread.start()

        print(f"🎙️  Streaming started (processing every {self.chunk_duration}s)")

    def stop_streaming(self) -> np.ndarray:
        """
        Stop streaming and return all recorded audio.

        Returns:
            Complete audio array
        """
        print("Stopping streaming...")

        # Set flag to stop recording FIRST
        self.is_recording = False

        # Disable callback to prevent further processing
        self.callback_function = None

        # Signal processing thread to stop (non-blocking)
        if hasattr(self, 'processing_thread'):
            try:
                self.audio_queue.put(None, block=False)
            except:
                pass

        # Stop the audio stream - do this AFTER signaling thread
        if self.stream:
            try:
                print("Stopping audio stream...")
                # Abort instead of stop to avoid blocking
                if hasattr(self.stream, 'abort'):
                    self.stream.abort()
                else:
                    self.stream.stop()
                print("Closing audio stream...")
                self.stream.close()
                print("Stream stopped and closed")
            except Exception as e:
                print(f"Error stopping stream: {e}")

        print("Returning audio...")

        # Return audio immediately
        if not self.all_audio:
            print("⚠️  No audio recorded")
            return np.array([])

        try:
            # Make a copy to avoid thread conflicts
            audio_copy = list(self.all_audio)
            if audio_copy:
                audio = np.concatenate(audio_copy, axis=0)
                print(f"✓ Streaming stopped ({len(audio)/self.sample_rate:.2f} seconds)")
                return audio
            else:
                return np.array([])
        except Exception as e:
            print(f"Error concatenating audio: {e}")
            return np.array([])

    def save_audio(self, audio_data: np.ndarray, filename: Optional[str] = None) -> str:
        """
        Save audio data to WAV file.

        Args:
            audio_data: NumPy array containing audio
            filename: Output filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        import wave
        import os

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

    def list_devices(self):
        """List all available audio devices."""
        print("\n=== Available Audio Devices ===")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            print(f"{i}: {device['name']} (in: {device['max_input_channels']}, out: {device['max_output_channels']})")
        return devices
