#!/usr/bin/env python3
"""Verify CallScribe installation and all Phase 4 features."""

import sys
from pathlib import Path


def check_imports():
    """Check if all required modules can be imported."""
    print("Checking imports...")

    required_modules = {
        'Core': [
            'sounddevice',
            'numpy',
            'whisper',
            'anthropic',
            'dotenv',
            'rich',
        ],
        'Web GUI': [
            'flask',
            'flask_socketio',
            'flask_cors',
            'qrcode',
        ],
        'CallScribe': [
            'callscribe.audio.capture',
            'callscribe.audio.streaming_capture',
            'callscribe.audio.pausable_capture',
            'callscribe.transcription.whisper_client',
            'callscribe.transcription.streaming_transcriber',
            'callscribe.transcription.simple_diarization',
            'callscribe.web.app',
            'callscribe.web.gui',
        ]
    }

    all_ok = True
    for category, modules in required_modules.items():
        print(f"\n{category}:")
        for module in modules:
            try:
                __import__(module)
                print(f"  ✓ {module}")
            except ImportError as e:
                print(f"  ✗ {module} - {e}")
                all_ok = False

    return all_ok


def check_files():
    """Check if all Phase 4 files exist."""
    print("\n\nChecking Phase 4 files...")

    required_files = {
        'Speaker Diarization': [
            'callscribe/transcription/simple_diarization.py',
            'SPEAKER_DIARIZATION_GUIDE.md',
        ],
        'Streaming': [
            'callscribe/audio/streaming_capture.py',
            'callscribe/transcription/streaming_transcriber.py',
            'STREAMING_GUIDE.md',
        ],
        'Pausable': [
            'callscribe/audio/pausable_capture.py',
            'PAUSABLE_GUIDE.md',
        ],
        'Web GUI': [
            'callscribe/web/__init__.py',
            'callscribe/web/app.py',
            'callscribe/web/gui.py',
            'callscribe/web/templates/index.html',
            'callscribe/__main__.py',
            'WEB_GUI_GUIDE.md',
        ],
        'Documentation': [
            'README.md',
            'QUICK_REFERENCE.md',
            'PHASE4_COMPLETE.md',
        ]
    }

    all_ok = True
    for category, files in required_files.items():
        print(f"\n{category}:")
        for file in files:
            path = Path(file)
            if path.exists():
                print(f"  ✓ {file}")
            else:
                print(f"  ✗ {file} - NOT FOUND")
                all_ok = False

    return all_ok


def check_configuration():
    """Check configuration."""
    print("\n\nChecking configuration...")

    env_file = Path('.env')
    if env_file.exists():
        print("  ✓ .env file exists")

        # Check if API key is set
        with open(env_file) as f:
            content = f.read()
            if 'ANTHROPIC_API_KEY' in content and 'your_api_key_here' not in content:
                print("  ✓ Anthropic API key configured")
            else:
                print("  ⚠ Anthropic API key not set (Claude analysis will not work)")
    else:
        print("  ✗ .env file not found")
        print("    Run: cp .env.example .env")
        return False

    return True


def test_cli_help():
    """Test CLI help command."""
    print("\n\nTesting CLI...")

    import subprocess

    try:
        result = subprocess.run(
            [sys.executable, '-m', 'callscribe.main', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and 'usage:' in result.stdout:
            print("  ✓ CLI help working")
            return True
        else:
            print("  ✗ CLI help failed")
            return False
    except Exception as e:
        print(f"  ✗ CLI test failed: {e}")
        return False


def test_gui_help():
    """Test GUI help command."""
    print("\nTesting Web GUI...")

    import subprocess

    try:
        result = subprocess.run(
            [sys.executable, '-m', 'callscribe', 'gui', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and 'CallScribe Web Interface' in result.stdout:
            print("  ✓ Web GUI launcher working")
            return True
        else:
            print("  ✗ Web GUI launcher failed")
            return False
    except Exception as e:
        print(f"  ✗ GUI test failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("CallScribe Installation Verification")
    print("=" * 60)

    results = {
        'Imports': check_imports(),
        'Files': check_files(),
        'Configuration': check_configuration(),
        'CLI': test_cli_help(),
        'GUI': test_gui_help(),
    }

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    all_passed = True
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check:20s} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All checks passed! CallScribe is ready to use.")
        print("\nQuick Start:")
        print("  Web GUI:  python -m callscribe gui")
        print("  CLI:      python -m callscribe.main")
        print("\nSee QUICK_REFERENCE.md for more commands.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review the output above.")
        print("See SETUP.md for installation instructions.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
