"""Automatic detection of video conferencing applications."""

import psutil
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class VideoApp:
    """Represents a detected video conferencing application."""
    name: str
    process_name: str
    detected: bool = False
    setup_hint: str = ""


class VideoChatDetector:
    """Detects running video conferencing applications and provides setup guidance."""

    VIDEO_APPS = {
        'zoom.us': VideoApp(
            name='Zoom',
            process_name='zoom.us',
            setup_hint='Zoom detected! For best results:\n'
                      '1. Set system output to Multi-Output Device (includes BlackHole)\n'
                      '2. In Zoom settings, set Speaker to Multi-Output Device\n'
                      '3. Set Microphone to your actual microphone\n'
                      '4. Enable "Video Conference Mode" in CallScribe'
        ),
        'Google Chrome': VideoApp(
            name='Google Meet',
            process_name='Google Chrome',
            setup_hint='Chrome detected (Google Meet)! For best results:\n'
                      '1. Set system output to Multi-Output Device (includes BlackHole)\n'
                      '2. In Meet settings, set Speaker to Multi-Output Device\n'
                      '3. Set Microphone to your actual microphone\n'
                      '4. Enable "Video Conference Mode" in CallScribe'
        ),
        'Microsoft Teams': VideoApp(
            name='Microsoft Teams',
            process_name='Microsoft Teams',
            setup_hint='Teams detected! For best results:\n'
                      '1. Set system output to Multi-Output Device (includes BlackHole)\n'
                      '2. In Teams settings, set Speaker to Multi-Output Device\n'
                      '3. Set Microphone to your actual microphone\n'
                      '4. Enable "Video Conference Mode" in CallScribe'
        ),
        'Webex': VideoApp(
            name='Cisco Webex',
            process_name='Webex',
            setup_hint='Webex detected! For best results:\n'
                      '1. Set system output to Multi-Output Device (includes BlackHole)\n'
                      '2. In Webex settings, set Speaker to Multi-Output Device\n'
                      '3. Set Microphone to your actual microphone\n'
                      '4. Enable "Video Conference Mode" in CallScribe'
        ),
        'Slack': VideoApp(
            name='Slack',
            process_name='Slack',
            setup_hint='Slack detected! For best results:\n'
                      '1. Set system output to Multi-Output Device (includes BlackHole)\n'
                      '2. In Slack settings, set Speaker to Multi-Output Device\n'
                      '3. Set Microphone to your actual microphone\n'
                      '4. Enable "Video Conference Mode" in CallScribe'
        ),
        'Discord': VideoApp(
            name='Discord',
            process_name='Discord',
            setup_hint='Discord detected! For best results:\n'
                      '1. Set system output to Multi-Output Device (includes BlackHole)\n'
                      '2. In Discord settings, set Output Device to Multi-Output Device\n'
                      '3. Set Input Device to your actual microphone\n'
                      '4. Enable "Video Conference Mode" in CallScribe'
        ),
        'Skype': VideoApp(
            name='Skype',
            process_name='Skype',
            setup_hint='Skype detected! For best results:\n'
                      '1. Set system output to Multi-Output Device (includes BlackHole)\n'
                      '2. In Skype settings, set Speakers to Multi-Output Device\n'
                      '3. Set Microphone to your actual microphone\n'
                      '4. Enable "Video Conference Mode" in CallScribe'
        ),
    }

    @classmethod
    def detect_running_apps(cls) -> List[VideoApp]:
        """
        Detect which video conferencing apps are currently running.

        Returns:
            List of detected VideoApp objects
        """
        detected = []
        running_processes = set()

        # Get all running process names
        for proc in psutil.process_iter(['name']):
            try:
                running_processes.add(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Check each video app
        for process_name, app_info in cls.VIDEO_APPS.items():
            if any(process_name.lower() in proc.lower() for proc in running_processes):
                app_info.detected = True
                detected.append(app_info)

        return detected

    @classmethod
    def get_setup_instructions(cls, detected_apps: Optional[List[VideoApp]] = None) -> str:
        """
        Get setup instructions for detected apps.

        Args:
            detected_apps: List of detected apps (will auto-detect if None)

        Returns:
            Formatted setup instructions
        """
        if detected_apps is None:
            detected_apps = cls.detect_running_apps()

        if not detected_apps:
            return cls._get_generic_instructions()

        instructions = "📹 Video Conferencing Apps Detected!\n\n"

        for app in detected_apps:
            instructions += f"═══ {app.name} ═══\n"
            instructions += f"{app.setup_hint}\n\n"

        instructions += cls._get_blackhole_check()

        return instructions

    @classmethod
    def _get_generic_instructions(cls) -> str:
        """Get generic instructions when no video apps detected."""
        return (
            "📹 Video Conference Mode\n\n"
            "To record video conferences (Zoom, Meet, Teams, etc.):\n\n"
            "1. Create Multi-Output Device in Audio MIDI Setup:\n"
            "   - Open Audio MIDI Setup (Applications > Utilities)\n"
            "   - Click '+' and create 'Multi-Output Device'\n"
            "   - Check both 'BlackHole 2ch' and your speakers\n\n"
            "2. In your video app settings:\n"
            "   - Set Speaker/Output to 'Multi-Output Device'\n"
            "   - Set Microphone/Input to your actual microphone\n\n"
            "3. In CallScribe:\n"
            "   - Enable 'Video Conference Mode'\n"
            "   - CallScribe will capture both:\n"
            "     • System audio (remote participants via BlackHole)\n"
            "     • Your microphone (your voice)\n\n"
            + cls._get_blackhole_check()
        )

    @classmethod
    def _get_blackhole_check(cls) -> str:
        """Add BlackHole installation check."""
        return (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Need BlackHole? Install with:\n"
            "  brew install blackhole-2ch\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )

    @classmethod
    def check_blackhole_installed(cls) -> bool:
        """
        Check if BlackHole is installed.

        Returns:
            True if BlackHole is installed
        """
        import sounddevice as sd

        devices = sd.query_devices()
        for device in devices:
            if 'blackhole' in device['name'].lower():
                return True
        return False

    @classmethod
    def get_blackhole_device_id(cls) -> Optional[int]:
        """
        Get the device ID for BlackHole.

        Returns:
            Device ID or None if not found
        """
        import sounddevice as sd

        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if 'blackhole' in device['name'].lower() and device['max_input_channels'] > 0:
                return i
        return None

    @classmethod
    def print_detection_report(cls):
        """Print a formatted detection report to console."""
        detected = cls.detect_running_apps()

        print("\n" + "="*60)
        print("  VIDEO CONFERENCING DETECTION REPORT")
        print("="*60)

        if detected:
            print(f"\n✓ Found {len(detected)} video conferencing app(s):\n")
            for app in detected:
                print(f"  • {app.name}")
        else:
            print("\n✗ No video conferencing apps currently detected")
            print("  (This is fine if you're not in a video call)")

        # Check BlackHole
        print("\n" + "-"*60)
        if cls.check_blackhole_installed():
            device_id = cls.get_blackhole_device_id()
            print("✓ BlackHole is installed")
            if device_id is not None:
                print(f"  Device ID: {device_id}")
        else:
            print("✗ BlackHole not found")
            print("  Install with: brew install blackhole-2ch")

        print("-"*60)

        # Show instructions
        if detected:
            print("\n" + cls.get_setup_instructions(detected))
        else:
            print("\n💡 Tip: Start your video call first, then run CallScribe")
            print("   to get app-specific setup instructions.")

        print("="*60 + "\n")
