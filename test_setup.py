#!/usr/bin/env python3
"""Test script to verify CallScribe installation."""

import sys
import os

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing package imports...\n")

    tests = {
        "sounddevice": "Audio capture",
        "numpy": "Array processing",
        "whisper": "Transcription (Whisper)",
        "anthropic": "Claude API",
        "rich": "Terminal UI",
        "dotenv": "Environment variables"
    }

    failed = []
    for package, description in tests.items():
        try:
            __import__(package)
            print(f"✓ {package:15} ({description})")
        except ImportError:
            print(f"✗ {package:15} ({description}) - MISSING")
            failed.append(package)

    print()

    if failed:
        print(f"❌ Missing packages: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All packages installed successfully!")
        return True


def test_ffmpeg():
    """Test FFmpeg installation."""
    print("\nTesting FFmpeg...\n")

    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ {version}")
            print("✅ FFmpeg is installed")
            return True
        else:
            print("✗ FFmpeg check failed")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found")
        print("Install with: brew install ffmpeg")
        return False


def test_env_file():
    """Test .env file configuration."""
    print("\nTesting environment configuration...\n")

    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("Run: cp .env.example .env")
        print("Then add your ANTHROPIC_API_KEY")
        return False

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("⚠️  .env file exists but ANTHROPIC_API_KEY not set")
        print("Edit .env and add your API key from: https://console.anthropic.com/")
        return False

    print("✓ .env file found")
    print("✓ ANTHROPIC_API_KEY is set")
    print("✅ Environment configured correctly")
    return True


def test_audio_devices():
    """Test audio device detection."""
    print("\nTesting audio devices...\n")

    try:
        import sounddevice as sd
        devices = sd.query_devices()

        print(f"Found {len(devices)} audio device(s):")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  [{i}] {device['name']} (input)")

        # Check for BlackHole
        blackhole_found = any('blackhole' in d['name'].lower() for d in devices)
        if blackhole_found:
            print("\n✅ BlackHole detected (for system audio capture)")
        else:
            print("\n⚠️  BlackHole not found")
            print("For system audio capture, install with: brew install blackhole-2ch")

        return True

    except Exception as e:
        print(f"❌ Error listing audio devices: {e}")
        return False


def test_whisper_model():
    """Test Whisper model loading (optional, can be slow)."""
    print("\nTesting Whisper model (this may take a minute on first run)...\n")

    try:
        import whisper
        print("Loading 'tiny' model for quick test...")
        model = whisper.load_model("tiny")
        print("✅ Whisper model loaded successfully")
        print("Note: First run downloads the model (~75MB)")
        return True
    except Exception as e:
        print(f"❌ Error loading Whisper model: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("CallScribe Installation Test")
    print("=" * 50)

    results = {
        "Imports": test_imports(),
        "FFmpeg": test_ffmpeg(),
        "Environment": test_env_file(),
        "Audio Devices": test_audio_devices(),
    }

    # Optional Whisper test
    response = input("\nTest Whisper model loading? (may download ~75MB) [y/N]: ")
    if response.lower() == 'y':
        results["Whisper Model"] = test_whisper_model()

    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! CallScribe is ready to use.")
        print("\nNext steps:")
        print("1. Run: python -m callscribe.main --list-devices")
        print("2. Run: python -m callscribe.main --show-config")
        print("3. Try a test recording!")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nRefer to SETUP.md for detailed instructions.")
    print("=" * 50)


if __name__ == "__main__":
    main()
