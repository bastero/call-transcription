"""Pausable audio capture for interactive recording sessions."""

import sounddevice as sd
import numpy as np
from typing import Optional, List
from datetime import datetime
import threading
import time


class PausableAudioCapture:
    """Audio capture with pause/resume capability."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        device: Optional[int] = None
    ):
        """
        Initialize pausable audio capture.

        Args:
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            device: Audio device index
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device

        self.audio_segments: List[np.ndarray] = []
        self.current_segment: List[np.ndarray] = []

        self.is_recording = False
        self.is_paused = False
        self.stream = None

        self.total_duration = 0.0
        self.pause_count = 0

        self.lock = threading.Lock()

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback function for audio stream."""
        if status:
            print(f"Audio status: {status}")

        with self.lock:
            if self.is_recording and not self.is_paused:
                self.current_segment.append(indata.copy())

    def start_recording(self):
        """Start recording audio."""
        with self.lock:
            self.audio_segments = []
            self.current_segment = []
            self.is_recording = True
            self.is_paused = False
            self.total_duration = 0.0
            self.pause_count = 0

        self.stream = sd.InputStream(
            device=self.device,
            channels=self.channels,
            samplerate=self.sample_rate,
            callback=self._audio_callback
        )
        self.stream.start()
        self.start_time = time.time()

        print(f"🎤 Recording started (Device: {self.device or 'default'})")
        print("   Press 'p' + ENTER to pause, 's' + ENTER to stop")

    def pause(self):
        """Pause recording (keeps stream active, stops capturing)."""
        with self.lock:
            if not self.is_paused and self.is_recording:
                self.is_paused = True

                # Save current segment
                if self.current_segment:
                    segment_audio = np.concatenate(self.current_segment, axis=0)
                    self.audio_segments.append(segment_audio)
                    segment_duration = len(segment_audio) / self.sample_rate
                    self.total_duration += segment_duration
                    self.current_segment = []

                self.pause_count += 1
                print(f"⏸️  Paused (Duration so far: {self.total_duration:.1f}s)")
                print("   Press 'r' + ENTER to resume, 's' + ENTER to stop")
                return True
        return False

    def resume(self):
        """Resume recording after pause."""
        with self.lock:
            if self.is_paused and self.is_recording:
                self.is_paused = False
                self.current_segment = []
                print(f"▶️  Resumed recording")
                print("   Press 'p' + ENTER to pause, 's' + ENTER to stop")
                return True
        return False

    def stop_recording(self) -> np.ndarray:
        """
        Stop recording and return all audio.

        Returns:
            Complete audio array
        """
        with self.lock:
            self.is_recording = False

            # Save final segment
            if self.current_segment:
                segment_audio = np.concatenate(self.current_segment, axis=0)
                self.audio_segments.append(segment_audio)
                segment_duration = len(segment_audio) / self.sample_rate
                self.total_duration += segment_duration

        if self.stream:
            self.stream.stop()
            self.stream.close()

        if not self.audio_segments:
            print("⚠️  No audio recorded")
            return np.array([])

        # Combine all segments
        complete_audio = np.concatenate(self.audio_segments, axis=0)

        print(f"✓ Recording stopped")
        print(f"  Total duration: {self.total_duration:.2f} seconds")
        print(f"  Paused {self.pause_count} time(s)")

        return complete_audio

    def get_status(self) -> dict:
        """
        Get current recording status.

        Returns:
            Dictionary with status information
        """
        with self.lock:
            current_duration = self.total_duration
            if self.current_segment:
                current_duration += len(np.concatenate(self.current_segment, axis=0)) / self.sample_rate

            return {
                "is_recording": self.is_recording,
                "is_paused": self.is_paused,
                "duration": current_duration,
                "pause_count": self.pause_count,
                "segments": len(self.audio_segments) + (1 if self.current_segment else 0)
            }

    def save_audio(self, audio_data: np.ndarray, filename: Optional[str] = None) -> str:
        """
        Save audio data to WAV file.

        Args:
            audio_data: Audio data to save
            filename: Output filename

        Returns:
            Path to saved file
        """
        import wave
        import os

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"

        os.makedirs("output", exist_ok=True)
        filepath = os.path.join("output", filename)

        # Normalize to 16-bit PCM
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


class InteractivePausableRecorder:
    """Interactive recorder with keyboard controls for pause/resume."""

    def __init__(self, capture: PausableAudioCapture):
        """
        Initialize interactive recorder.

        Args:
            capture: PausableAudioCapture instance
        """
        self.capture = capture
        self.running = False

    def start_interactive(self):
        """Start interactive recording session."""
        self.capture.start_recording()
        self.running = True

        while self.running:
            try:
                command = input().strip().lower()

                if command == 'p':
                    self.capture.pause()
                elif command == 'r':
                    self.capture.resume()
                elif command == 's':
                    print("Stopping recording...")
                    self.running = False
                    break
                elif command == 'status':
                    status = self.capture.get_status()
                    print(f"\n📊 Status:")
                    print(f"   Recording: {'Yes' if status['is_recording'] else 'No'}")
                    print(f"   Paused: {'Yes' if status['is_paused'] else 'No'}")
                    print(f"   Duration: {status['duration']:.1f}s")
                    print(f"   Segments: {status['segments']}")
                    print(f"   Pauses: {status['pause_count']}\n")
                else:
                    if command:  # Ignore empty input
                        print("Commands: 'p' (pause), 'r' (resume), 's' (stop), 'status'")

            except KeyboardInterrupt:
                print("\n\nStopping recording...")
                self.running = False
                break

        return self.capture.stop_recording()
