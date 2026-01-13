"""Dual-stream audio capture for video conferencing."""

import sounddevice as sd
import numpy as np
import queue
import threading
from typing import Optional, Tuple
from datetime import datetime


class DualStreamCapture:
    """
    Captures audio from two sources simultaneously (microphone + system audio).

    Perfect for video conferencing where you need to record:
    - Your voice (from microphone)
    - Remote participants (from system audio via BlackHole)
    """

    def __init__(
        self,
        mic_device: Optional[int] = None,
        system_device: Optional[int] = None,
        sample_rate: int = 16000,
        channels: int = 1
    ):
        """
        Initialize dual-stream audio capture.

        Args:
            mic_device: Microphone device index (None for default)
            system_device: System audio device index (BlackHole)
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
        """
        self.mic_device = mic_device
        self.system_device = system_device
        self.sample_rate = sample_rate
        self.channels = channels

        self.mic_queue = queue.Queue()
        self.system_queue = queue.Queue()
        self.is_recording = False
        self.mic_stream = None
        self.system_stream = None
        self.mic_audio = []
        self.system_audio = []

    def _mic_callback(self, indata, frames, time, status):
        """Callback for microphone stream."""
        if status:
            print(f"Mic status: {status}")
        if self.is_recording:
            self.mic_queue.put(indata.copy())
            self.mic_audio.append(indata.copy())

    def _system_callback(self, indata, frames, time, status):
        """Callback for system audio stream."""
        if status:
            print(f"System status: {status}")
        if self.is_recording:
            self.system_queue.put(indata.copy())
            self.system_audio.append(indata.copy())

    def start_recording(self):
        """Start recording from both streams."""
        self.mic_queue = queue.Queue()
        self.system_queue = queue.Queue()
        self.mic_audio = []
        self.system_audio = []
        self.is_recording = True

        # Use consistent blocksize for both streams to ensure synchronized accumulation
        # 1600 samples at 16kHz = 100ms chunks (matches system audio default)
        blocksize = 1600

        # Start microphone stream
        self.mic_stream = sd.InputStream(
            device=self.mic_device,
            channels=self.channels,
            samplerate=self.sample_rate,
            blocksize=blocksize,
            callback=self._mic_callback
        )
        self.mic_stream.start()

        # Start system audio stream (BlackHole)
        self.system_stream = sd.InputStream(
            device=self.system_device,
            channels=self.channels,
            samplerate=self.sample_rate,
            blocksize=blocksize,
            callback=self._system_callback
        )
        self.system_stream.start()

        print("🎙️  Dual-stream recording started")
        print("   • Microphone: Capturing your voice")
        print("   • System Audio: Capturing remote participants")

    def stop_recording(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Stop recording and return audio from both streams.

        Returns:
            Tuple of (combined_audio, mic_audio, system_audio)
        """
        print("Stopping dual-stream recording...")

        # Set flag first
        self.is_recording = False

        # Stop streams
        if self.mic_stream:
            try:
                if hasattr(self.mic_stream, 'abort'):
                    self.mic_stream.abort()
                else:
                    self.mic_stream.stop()
                self.mic_stream.close()
            except Exception as e:
                print(f"Error stopping mic stream: {e}")

        if self.system_stream:
            try:
                if hasattr(self.system_stream, 'abort'):
                    self.system_stream.abort()
                else:
                    self.system_stream.stop()
                self.system_stream.close()
            except Exception as e:
                print(f"Error stopping system stream: {e}")

        # Process audio
        if not self.mic_audio or not self.system_audio:
            print("⚠️  No audio recorded from one or both streams")
            return np.array([]), np.array([]), np.array([])

        try:
            # Concatenate audio from each stream
            mic_audio = np.concatenate(self.mic_audio, axis=0)
            system_audio = np.concatenate(self.system_audio, axis=0)

            # Make them the same length (pad shorter one with zeros)
            max_len = max(len(mic_audio), len(system_audio))
            if len(mic_audio) < max_len:
                mic_audio = np.pad(mic_audio, ((0, max_len - len(mic_audio)), (0, 0)), mode='constant')
            if len(system_audio) < max_len:
                system_audio = np.pad(system_audio, ((0, max_len - len(system_audio)), (0, 0)), mode='constant')

            # Mix the two streams (average them)
            combined_audio = (mic_audio + system_audio) / 2.0

            duration = len(combined_audio) / self.sample_rate
            print(f"✓ Dual-stream recording complete ({duration:.2f} seconds)")
            print(f"   • Microphone: {len(mic_audio)/self.sample_rate:.2f}s")
            print(f"   • System Audio: {len(system_audio)/self.sample_rate:.2f}s")
            print(f"   • Combined: {duration:.2f}s")

            return combined_audio, mic_audio, system_audio

        except Exception as e:
            print(f"Error processing audio: {e}")
            return np.array([]), np.array([]), np.array([])

    def save_audio(
        self,
        combined_audio: np.ndarray,
        mic_audio: Optional[np.ndarray] = None,
        system_audio: Optional[np.ndarray] = None,
        base_filename: Optional[str] = None
    ) -> dict:
        """
        Save audio data to WAV files.

        Args:
            combined_audio: Mixed audio from both streams
            mic_audio: Microphone audio only (optional)
            system_audio: System audio only (optional)
            base_filename: Base filename (auto-generated if None)

        Returns:
            Dictionary with paths to saved files
        """
        import wave
        import os

        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"recording_{timestamp}"

        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)

        saved_files = {}

        # Save combined audio
        if len(combined_audio) > 0:
            filepath = os.path.join("output", f"{base_filename}_combined.wav")
            self._save_wav(combined_audio, filepath)
            saved_files['combined'] = filepath
            print(f"💾 Combined audio saved: {filepath}")

        # Save microphone audio
        if mic_audio is not None and len(mic_audio) > 0:
            filepath = os.path.join("output", f"{base_filename}_mic.wav")
            self._save_wav(mic_audio, filepath)
            saved_files['mic'] = filepath
            print(f"💾 Microphone audio saved: {filepath}")

        # Save system audio
        if system_audio is not None and len(system_audio) > 0:
            filepath = os.path.join("output", f"{base_filename}_system.wav")
            self._save_wav(system_audio, filepath)
            saved_files['system'] = filepath
            print(f"💾 System audio saved: {filepath}")

        return saved_files

    def _save_wav(self, audio_data: np.ndarray, filepath: str):
        """Save audio data to WAV file."""
        import wave

        # Normalize audio to 16-bit PCM
        audio_normalized = np.int16(audio_data * 32767)

        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_normalized.tobytes())

    def list_devices(self):
        """List all available audio devices."""
        print("\n=== Available Audio Devices ===")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            device_type = []
            if device['max_input_channels'] > 0:
                device_type.append("INPUT")
            if device['max_output_channels'] > 0:
                device_type.append("OUTPUT")

            # Highlight BlackHole and microphones
            marker = ""
            if 'blackhole' in device['name'].lower():
                marker = " ← BlackHole (System Audio)"
            elif device['max_input_channels'] > 0 and 'built-in' in device['name'].lower():
                marker = " ← Built-in Microphone"

            print(f"{i}: {device['name']} ({'/'.join(device_type)}){marker}")

        return devices

    @staticmethod
    def find_blackhole_device() -> Optional[int]:
        """
        Find BlackHole device automatically.

        Returns:
            Device ID or None if not found
        """
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if 'blackhole' in device['name'].lower() and device['max_input_channels'] > 0:
                return i
        return None

    @staticmethod
    def find_default_mic() -> Optional[int]:
        """
        Find default microphone device.

        Returns:
            Device ID or None
        """
        try:
            return sd.default.device[0]  # Input device
        except:
            return None


class StreamingDualCapture(DualStreamCapture):
    """
    Dual-stream capture with real-time streaming transcription.

    Processes audio chunks every few seconds while recording continues.
    """

    def __init__(
        self,
        mic_device: Optional[int] = None,
        system_device: Optional[int] = None,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_duration: float = 5.0
    ):
        """
        Initialize streaming dual-stream capture.

        Args:
            mic_device: Microphone device index
            system_device: System audio device index
            sample_rate: Sample rate in Hz
            channels: Number of channels
            chunk_duration: Duration of each processing chunk in seconds
        """
        super().__init__(mic_device, system_device, sample_rate, channels)
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.callback_function = None
        self.processing_thread = None

    def _process_chunks(self):
        """Process combined audio chunks in a separate thread."""
        mic_buffer = np.array([]).reshape(0, self.channels)
        system_buffer = np.array([]).reshape(0, self.channels)

        while self.is_recording:
            try:
                # Get audio from both queues
                mic_chunk = None
                system_chunk = None

                try:
                    mic_chunk = self.mic_queue.get(timeout=0.1)
                except queue.Empty:
                    pass

                try:
                    system_chunk = self.system_queue.get(timeout=0.1)
                except queue.Empty:
                    pass

                # Add to buffers (only if we got data)
                if mic_chunk is not None:
                    mic_buffer = np.vstack([mic_buffer, mic_chunk])
                if system_chunk is not None:
                    system_buffer = np.vstack([system_buffer, system_chunk])

                # When buffers reach chunk_size, process them
                if len(mic_buffer) >= self.chunk_size and len(system_buffer) >= self.chunk_size:
                    # Take chunk_size samples from each
                    mic_audio = mic_buffer[:self.chunk_size]
                    system_audio = system_buffer[:self.chunk_size]
                    mic_buffer = mic_buffer[self.chunk_size:]
                    system_buffer = system_buffer[self.chunk_size:]

                    # Mix them
                    combined = (mic_audio + system_audio) / 2.0

                    # Call callback if set and still recording
                    if self.callback_function and self.is_recording:
                        try:
                            self.callback_function(combined)
                        except Exception as e:
                            print(f"Error in streaming callback: {e}")

            except Exception as e:
                print(f"Error in processing thread: {e}")
                continue

        # Process remaining buffers
        if len(mic_buffer) > 0 and len(system_buffer) > 0 and self.callback_function:
            # Make them same length
            max_len = max(len(mic_buffer), len(system_buffer))
            if len(mic_buffer) < max_len:
                mic_buffer = np.pad(mic_buffer, ((0, max_len - len(mic_buffer)), (0, 0)), mode='constant')
            if len(system_buffer) < max_len:
                system_buffer = np.pad(system_buffer, ((0, max_len - len(system_buffer)), (0, 0)), mode='constant')

            combined = (mic_buffer + system_buffer) / 2.0
            self.callback_function(combined)

    def start_streaming(self, callback):
        """
        Start streaming with real-time processing.

        Args:
            callback: Function to call with each combined audio chunk
        """
        self.callback_function = callback
        self.start_recording()

        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_chunks, daemon=True)
        self.processing_thread.start()

        print(f"   • Processing every {self.chunk_duration}s")

    def stop_streaming(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Stop streaming and return all audio.

        Returns:
            Tuple of (combined_audio, mic_audio, system_audio)
        """
        # Disable callback first
        self.callback_function = None

        # Signal processing thread
        if self.processing_thread:
            try:
                self.mic_queue.put(None, block=False)
                self.system_queue.put(None, block=False)
            except:
                pass

        # Call parent stop method
        return self.stop_recording()
