"""Main CallScribe application."""

import argparse
import sys
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from callscribe.audio.capture import AudioCapture
from callscribe.audio.dual_stream_capture import DualStreamCapture
from callscribe.transcription.whisper_client import WhisperTranscriber
from callscribe.analysis.claude_client import ClaudeAnalyzer
from callscribe.output.exporter import TranscriptExporter
from callscribe.utils.config import get_config
from callscribe.utils.video_chat_detector import VideoChatDetector

console = Console()


def display_banner():
    """Display application banner."""
    banner = """
    ╔═══════════════════════════════════════╗
    ║         CallScribe v1.0               ║
    ║  AI-Powered Call Transcription        ║
    ╚═══════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def list_audio_devices():
    """List available audio devices and exit."""
    console.print("\n[bold cyan]Available Audio Devices:[/bold cyan]\n")
    capture = AudioCapture()
    capture.list_devices()
    sys.exit(0)


def run_pausable_recording(args):
    """Run recording with pause/resume capability."""
    from callscribe.audio.pausable_capture import PausableAudioCapture, InteractivePausableRecorder

    config = get_config()

    # Only validate API key if analysis is not skipped
    if not args.skip_analysis and not config.validate():
        console.print("[red]Configuration error. Please check your .env file.[/red]")
        sys.exit(1)

    console.print("\n[cyan]Initializing Pausable Recording Mode...[/cyan]\n")

    # Initialize components
    pausable_capture = PausableAudioCapture(
        sample_rate=config.sample_rate,
        channels=config.channels,
        device=args.device
    )

    transcriber = WhisperTranscriber(model_name=args.model or config.whisper_model)
    exporter = TranscriptExporter(output_dir=args.output_dir)

    # Show instructions
    console.print(Panel.fit(
        "[yellow]Interactive Recording Mode[/yellow]\n\n"
        "Controls:\n"
        "  • Type 'p' + ENTER to [bold]pause[/bold]\n"
        "  • Type 'r' + ENTER to [bold]resume[/bold]\n"
        "  • Type 's' + ENTER to [bold]stop[/bold]\n"
        "  • Type 'status' + ENTER for current status\n\n"
        "Press ENTER to start recording...",
        title="Step 1: Audio Capture (Pausable)"
    ))
    input()

    # Start interactive recording
    recorder = InteractivePausableRecorder(pausable_capture)
    audio_data = recorder.start_interactive()

    if len(audio_data) == 0:
        console.print("[red]No audio recorded. Exiting.[/red]")
        sys.exit(1)

    # Save audio file if requested or if diarization is enabled
    audio_file = None
    if args.save_audio or args.diarize:
        audio_file = pausable_capture.save_audio(audio_data)

    # Step 2: Transcribe
    console.print("\n")
    console.print(Panel.fit(
        "[cyan]Transcribing audio with Whisper...[/cyan]",
        title="Step 2: Transcription"
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Transcribing...", total=None)
        result = transcriber.transcribe_array(audio_data, sample_rate=config.sample_rate)
        progress.update(task, completed=True)

    # Step 2.5: Speaker Diarization (if enabled)
    if args.diarize:
        from callscribe.transcription.simple_diarization import SimpleSpeakerDiarizer

        console.print("\n")
        console.print(Panel.fit(
            "[cyan]Identifying speakers...[/cyan]",
            title="Step 2.5: Speaker Diarization"
        ))

        diarizer = SimpleSpeakerDiarizer()

        # Detect speakers from transcript segments
        aligned_segments = diarizer.detect_speakers_from_segments(
            result.get("segments", []),
            num_speakers=args.num_speakers
        )

        if aligned_segments:
            # Format transcript with speaker labels
            transcript = diarizer.format_transcript_with_speakers(
                aligned_segments,
                include_timestamps=args.timestamps
            )

            # Get speaker stats
            speaker_stats = diarizer.get_speaker_stats(aligned_segments)
            num_speakers = diarizer.detect_num_speakers(aligned_segments)

            console.print(f"\n✓ Identified {num_speakers} speaker(s)")
            for speaker, stats in speaker_stats.items():
                console.print(f"  {speaker}: {stats['total_time']:.1f}s, {stats['word_count']} words")
        else:
            transcript = transcriber.format_transcript(result, include_timestamps=args.timestamps)
    else:
        transcript = transcriber.format_transcript(result, include_timestamps=args.timestamps)

    # Display transcript
    console.print("\n")
    console.print(Panel(transcript, title="[bold green]Transcript[/bold green]", border_style="green"))

    # Save transcript
    transcript_file = exporter.save_transcript(
        transcript,
        filename=args.output,
        format=args.format
    )

    # Step 3: Analyze with Claude (if not skipped)
    analysis = None
    if not args.skip_analysis:
        console.print("\n")
        console.print(Panel.fit(
            "[cyan]Analyzing transcript with Claude...[/cyan]",
            title="Step 3: AI Analysis"
        ))

        try:
            analyzer = ClaudeAnalyzer(api_key=config.anthropic_api_key, model=config.claude_model)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Analyzing...", total=None)
                analysis = analyzer.analyze_transcript(transcript)
                progress.update(task, completed=True)

            # Display analysis
            console.print("\n")
            console.print(Panel(analysis, title="[bold magenta]Claude Analysis[/bold magenta]", border_style="magenta"))

            # Save analysis
            exporter.save_analysis(analysis)

            # Save complete report
            if args.full_report:
                status = pausable_capture.get_status()
                metadata = {
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Duration": f"{status['duration']:.2f} seconds",
                    "Pauses": status['pause_count'],
                    "Model": args.model or config.whisper_model,
                    "Sample Rate": f"{config.sample_rate} Hz"
                }
                exporter.save_complete_report(transcript, analysis, metadata)

        except Exception as e:
            console.print(f"[red]Error during analysis: {e}[/red]")

    # Summary
    status = pausable_capture.get_status()
    console.print("\n")
    console.print(Panel.fit(
        f"[green]✓ Recording complete![/green]\n"
        f"Duration: {status['duration']:.2f} seconds\n"
        f"Paused: {status['pause_count']} time(s)\n"
        f"Transcript saved to: {transcript_file}\n"
        + (f"Audio saved to: {audio_file}\n" if audio_file else "")
        + (f"Analysis completed" if analysis else ""),
        title="Summary"
    ))


def run_streaming_transcription(args):
    """Run real-time streaming transcription workflow."""
    from callscribe.audio.streaming_capture import StreamingAudioCapture
    from callscribe.transcription.streaming_transcriber import (
        StreamingTranscriber,
        LiveTranscriptDisplay,
        create_streaming_callback
    )

    config = get_config()

    console.print("\n[cyan]Initializing Streaming Mode...[/cyan]\n")

    # Use tiny model for real-time (fastest)
    model = args.model if args.model else "tiny"
    if model not in ["tiny", "base"]:
        console.print(f"[yellow]⚠️  Using '{model}' may be too slow for real-time.[/yellow]")
        console.print("[yellow]   Switching to 'tiny' for better performance.[/yellow]")
        model = "tiny"

    # Initialize components
    streaming_capture = StreamingAudioCapture(
        sample_rate=config.sample_rate,
        channels=config.channels,
        device=args.device,
        chunk_duration=5.0  # Process every 5 seconds
    )

    transcriber = StreamingTranscriber(model_name=model)
    display = LiveTranscriptDisplay()
    exporter = TranscriptExporter(output_dir=args.output_dir)

    # Create callback
    chunk_counter = [0]
    callback = create_streaming_callback(transcriber, display, chunk_counter)

    console.print(Panel.fit(
        "[yellow]Real-time transcription mode[/yellow]\n"
        "Audio will be transcribed every 5 seconds\n"
        "Press ENTER to start...",
        title="Streaming Mode"
    ))
    input()

    # Start streaming
    streaming_capture.start_streaming(callback)

    console.print(Panel.fit(
        "[red]🔴 LIVE - Transcribing in real-time[/red]\n"
        "Speak naturally, transcripts appear below\n"
        "Press ENTER to stop...",
        title="Recording"
    ))
    input()

    # Stop streaming
    audio_data = streaming_capture.stop_streaming()

    # Get full transcript
    full_transcript = transcriber.get_full_transcript()

    console.print("\n")
    console.print(Panel(full_transcript, title="[bold green]Complete Transcript[/bold green]", border_style="green"))

    # Save audio if requested
    if args.save_audio and len(audio_data) > 0:
        from callscribe.audio.capture import AudioCapture
        temp_capture = AudioCapture()
        audio_file = temp_capture.save_audio(audio_data)

    # Save transcript
    transcript_file = exporter.save_transcript(
        full_transcript,
        filename=args.output,
        format=args.format
    )

    # Optional Claude analysis
    if not args.skip_analysis and full_transcript:
        console.print("\n")
        console.print(Panel.fit(
            "[cyan]Analyzing complete transcript with Claude...[/cyan]",
            title="AI Analysis"
        ))

        try:
            if not config.validate():
                console.print("[yellow]Skipping analysis - API key not configured[/yellow]")
            else:
                analyzer = ClaudeAnalyzer(api_key=config.anthropic_api_key, model=config.claude_model)
                analysis = analyzer.analyze_transcript(full_transcript)

                console.print("\n")
                console.print(Panel(analysis, title="[bold magenta]Claude Analysis[/bold magenta]", border_style="magenta"))

                exporter.save_analysis(analysis)
        except Exception as e:
            console.print(f"[red]Error during analysis: {e}[/red]")

    console.print("\n")
    console.print(Panel.fit(
        f"[green]✓ Streaming transcription complete![/green]\n"
        f"Processed {chunk_counter[0]} chunks\n"
        f"Transcript saved to: {transcript_file}",
        title="Summary"
    ))


def run_transcription(args):
    """Run the standard (non-streaming) transcription workflow."""
    # Load configuration
    config = get_config()

    # Only validate API key if analysis is not skipped
    if not args.skip_analysis and not config.validate():
        console.print("[red]Configuration error. Please check your .env file.[/red]")
        sys.exit(1)

    if args.show_config:
        config.display()
        return

    # Initialize components
    console.print("\n[cyan]Initializing CallScribe...[/cyan]\n")

    audio_capture = AudioCapture(
        sample_rate=config.sample_rate,
        channels=config.channels,
        device=args.device
    )

    transcriber = WhisperTranscriber(model_name=args.model or config.whisper_model)

    exporter = TranscriptExporter(output_dir=args.output_dir)

    # Step 1: Record Audio
    console.print(Panel.fit(
        "[yellow]Press ENTER to start recording...[/yellow]",
        title="Step 1: Audio Capture"
    ))
    input()

    audio_capture.start_recording()

    console.print(Panel.fit(
        "[red]Recording in progress...\nPress ENTER to stop recording[/red]",
        title="Recording"
    ))
    input()

    audio_data = audio_capture.stop_recording()

    if len(audio_data) == 0:
        console.print("[red]No audio recorded. Exiting.[/red]")
        sys.exit(1)

    # Save audio file if requested or if diarization is enabled
    audio_file = None
    if args.save_audio or args.diarize:
        audio_file = audio_capture.save_audio(audio_data)

    # Step 2: Transcribe
    console.print("\n")
    console.print(Panel.fit(
        "[cyan]Transcribing audio with Whisper...[/cyan]",
        title="Step 2: Transcription"
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Transcribing...", total=None)
        result = transcriber.transcribe_array(audio_data, sample_rate=config.sample_rate)
        progress.update(task, completed=True)

    # Step 2.5: Speaker Diarization (if enabled)
    if args.diarize:
        from callscribe.transcription.simple_diarization import SimpleSpeakerDiarizer

        console.print("\n")
        console.print(Panel.fit(
            "[cyan]Identifying speakers...[/cyan]",
            title="Step 2.5: Speaker Diarization"
        ))

        diarizer = SimpleSpeakerDiarizer()

        # Detect speakers from transcript segments
        aligned_segments = diarizer.detect_speakers_from_segments(
            result.get("segments", []),
            num_speakers=args.num_speakers
        )

        if aligned_segments:
            # Format transcript with speaker labels
            transcript = diarizer.format_transcript_with_speakers(
                aligned_segments,
                include_timestamps=args.timestamps
            )

            # Get speaker stats
            speaker_stats = diarizer.get_speaker_stats(aligned_segments)
            num_speakers = diarizer.detect_num_speakers(aligned_segments)

            console.print(f"\n✓ Identified {num_speakers} speaker(s)")
            for speaker, stats in speaker_stats.items():
                console.print(f"  {speaker}: {stats['total_time']:.1f}s, {stats['word_count']} words")
        else:
            transcript = transcriber.format_transcript(result, include_timestamps=args.timestamps)
    else:
        transcript = transcriber.format_transcript(result, include_timestamps=args.timestamps)

    # Display transcript
    console.print("\n")
    console.print(Panel(transcript, title="[bold green]Transcript[/bold green]", border_style="green"))

    # Save transcript
    transcript_file = exporter.save_transcript(
        transcript,
        filename=args.output,
        format=args.format
    )

    # Step 3: Analyze with Claude (if not skipped)
    analysis = None
    if not args.skip_analysis:
        console.print("\n")
        console.print(Panel.fit(
            "[cyan]Analyzing transcript with Claude...[/cyan]",
            title="Step 3: AI Analysis"
        ))

        try:
            analyzer = ClaudeAnalyzer(api_key=config.anthropic_api_key, model=config.claude_model)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Analyzing...", total=None)
                analysis = analyzer.analyze_transcript(transcript)
                progress.update(task, completed=True)

            # Display analysis
            console.print("\n")
            console.print(Panel(analysis, title="[bold magenta]Claude Analysis[/bold magenta]", border_style="magenta"))

            # Save analysis
            exporter.save_analysis(analysis)

            # Save complete report
            if args.full_report:
                metadata = {
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Duration": f"{len(audio_data)/config.sample_rate:.2f} seconds",
                    "Model": args.model or config.whisper_model,
                    "Sample Rate": f"{config.sample_rate} Hz"
                }
                exporter.save_complete_report(transcript, analysis, metadata)

        except Exception as e:
            console.print(f"[red]Error during analysis: {e}[/red]")

    # Summary
    console.print("\n")
    console.print(Panel.fit(
        f"[green]✓ Transcription complete![/green]\n"
        f"Transcript saved to: {transcript_file}\n"
        + (f"Audio saved to: {audio_file}\n" if audio_file else "")
        + (f"Analysis completed" if analysis else ""),
        title="Summary"
    ))


def run_video_conference_recording(args):
    """Run video conference recording with dual-stream capture."""
    config = get_config()

    # Only validate API key if analysis is not skipped
    if not args.skip_analysis and not config.validate():
        console.print("[red]Configuration error. Please check your .env file.[/red]")
        sys.exit(1)

    console.print("\n[cyan]📹 Video Conference Recording Mode[/cyan]\n")

    # Detect video apps
    VideoChatDetector.print_detection_report()

    # Check BlackHole
    if not VideoChatDetector.check_blackhole_installed():
        console.print("[red]❌ BlackHole not found![/red]")
        console.print("[yellow]Install with: brew install blackhole-2ch[/yellow]")
        sys.exit(1)

    # Find devices
    mic_device = args.device  # User's microphone
    system_device = args.system_device if hasattr(args, 'system_device') else VideoChatDetector.get_blackhole_device_id()

    if system_device is None:
        console.print("[red]❌ Could not find BlackHole device[/red]")
        sys.exit(1)

    console.print(f"[green]✓ Microphone device: {mic_device or 'Default'}[/green]")
    console.print(f"[green]✓ System audio device (BlackHole): {system_device}[/green]\n")

    # Initialize dual-stream capture
    dual_capture = DualStreamCapture(
        mic_device=mic_device,
        system_device=system_device,
        sample_rate=config.sample_rate,
        channels=config.channels
    )

    console.print(Panel.fit(
        "[yellow]Dual-Stream Video Conference Recording[/yellow]\n\n"
        "This mode captures:\n"
        "  • Your voice (from microphone)\n"
        "  • Remote participants (from system audio)\n\n"
        "Make sure your video app is configured:\n"
        "  • Output/Speaker: Multi-Output Device (with BlackHole)\n"
        "  • Input/Microphone: Your actual microphone\n\n"
        "Press ENTER to start recording...",
        title="Step 1: Dual-Stream Audio Capture"
    ))
    input()

    # Start recording
    dual_capture.start_recording()

    console.print(Panel.fit(
        "[red]🔴 RECORDING (Both Streams)[/red]\n"
        "Capturing audio from microphone and system...\n"
        "Press ENTER to stop...",
        title="Recording"
    ))
    input()

    # Stop recording
    combined_audio, mic_audio, system_audio = dual_capture.stop_recording()

    if len(combined_audio) == 0:
        console.print("[red]No audio recorded. Exiting.[/red]")
        sys.exit(1)

    # Save audio files if requested
    audio_files = {}
    if args.save_audio:
        console.print("\n[cyan]Saving audio files...[/cyan]")
        audio_files = dual_capture.save_audio(combined_audio, mic_audio, system_audio)

    # Step 2: Transcribe
    console.print("\n")
    console.print(Panel.fit(
        "[cyan]Transcribing combined audio with Whisper...[/cyan]",
        title="Step 2: Transcription"
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Transcribing...", total=None)
        transcriber = WhisperTranscriber(model_name=args.model or config.whisper_model)
        result = transcriber.transcribe_array(combined_audio, config.sample_rate)
        transcript = result.get('text', '')
        progress.update(task, completed=True)

    console.print("\n")
    console.print(Panel(transcript, title="[bold green]Transcript[/bold green]", border_style="green"))

    # Step 3: Optional Analysis
    analysis = None
    if not args.skip_analysis and transcript:
        console.print("\n")
        console.print(Panel.fit(
            "[cyan]Analyzing transcript with Claude...[/cyan]",
            title="Step 3: AI Analysis"
        ))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing...", total=None)
            analyzer = ClaudeAnalyzer(api_key=config.anthropic_api_key, model=config.claude_model)
            analysis = analyzer.analyze_transcript(transcript)
            progress.update(task, completed=True)

        console.print("\n")
        console.print(Panel(analysis, title="[bold cyan]Analysis[/bold cyan]", border_style="cyan"))

    # Step 4: Save Results
    exporter = TranscriptExporter(output_dir=args.output_dir)

    transcript_file = exporter.save_transcript(
        transcript,
        filename=args.output,
        format=args.format
    )

    analysis_file = None
    if analysis:
        analysis_file = exporter.save_analysis(analysis)

    # Final summary
    console.print("\n")
    console.print(Panel.fit(
        f"[green]✓ Video conference recording complete![/green]\n\n"
        f"Duration: {len(combined_audio)/config.sample_rate:.2f} seconds\n"
        f"Transcript: {transcript_file}\n"
        + (f"Analysis: {analysis_file}\n" if analysis_file else "")
        + (f"Audio files: {len(audio_files)} saved\n" if audio_files else ""),
        title="Summary"
    ))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CallScribe - AI-Powered Call Transcription & Analysis"
    )

    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio devices and exit"
    )

    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="Audio device index to use (see --list-devices)"
    )

    parser.add_argument(
        "--model",
        type=str,
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model to use (default: from .env)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output filename for transcript"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Output directory (default: output/)"
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["txt", "md", "json"],
        default="txt",
        help="Output format (default: txt)"
    )

    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="Include timestamps in transcript"
    )

    parser.add_argument(
        "--save-audio",
        action="store_true",
        help="Save recorded audio to file"
    )

    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Enable real-time streaming transcription (uses 'tiny' model)"
    )

    parser.add_argument(
        "--pausable",
        action="store_true",
        help="Enable pause/resume controls during recording"
    )

    parser.add_argument(
        "--video-conference",
        action="store_true",
        help="Enable video conference mode (dual-stream: mic + system audio)"
    )

    parser.add_argument(
        "--system-device",
        type=int,
        default=None,
        help="System audio device index (BlackHole) for video conference mode"
    )

    parser.add_argument(
        "--detect-video-apps",
        action="store_true",
        help="Detect running video conferencing apps and show setup instructions"
    )

    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Skip Claude analysis"
    )

    parser.add_argument(
        "--full-report",
        action="store_true",
        help="Generate complete report with metadata"
    )

    parser.add_argument(
        "--diarize",
        action="store_true",
        help="Enable speaker diarization (identifies different speakers)"
    )

    parser.add_argument(
        "--num-speakers",
        type=int,
        default=None,
        help="Expected number of speakers (optional hint for diarization)"
    )

    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show current configuration and exit"
    )

    args = parser.parse_args()

    display_banner()

    if args.list_devices:
        list_audio_devices()

    if args.detect_video_apps:
        VideoChatDetector.print_detection_report()
        sys.exit(0)

    # Route to appropriate workflow
    if args.video_conference:
        run_video_conference_recording(args)
    elif args.streaming:
        run_streaming_transcription(args)
    elif args.pausable:
        run_pausable_recording(args)
    else:
        run_transcription(args)


if __name__ == "__main__":
    main()
