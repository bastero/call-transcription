"""Flask web application for CallScribe."""

import os
import sys
import signal
import socket
import threading
import qrcode
import io
import base64
import numpy as np
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS

from callscribe.utils.config import Config
from callscribe.utils.video_chat_detector import VideoChatDetector
from callscribe.audio.capture import AudioCapture
from callscribe.audio.streaming_capture import StreamingAudioCapture
from callscribe.audio.pausable_capture import PausableAudioCapture
from callscribe.audio.dual_stream_capture import DualStreamCapture, StreamingDualCapture
from callscribe.transcription.whisper_client import WhisperTranscriber
from callscribe.transcription.streaming_transcriber import StreamingTranscriber
from callscribe.transcription.simple_diarization import SimpleSpeakerDiarizer
from callscribe.analysis.claude_client import ClaudeAnalyzer
from callscribe.output.exporter import TranscriptExporter


app = Flask(__name__)
app.config['SECRET_KEY'] = 'callscribe-secret-key-change-in-production'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
recording_state = {
    'active': False,
    'mode': None,  # 'standard', 'streaming', 'pausable'
    'paused': False,
    'duration': 0,
    'segments': 0,
    'transcript_chunks': [],
    'audio_capture': None,
    'status': 'idle',
    'options': {}  # Store options for dynamic updates
}

config = Config()


def get_local_ip():
    """Get local IP address for network access, preferring WiFi/Ethernet over VPN."""
    import netifaces

    try:
        # Get all network interfaces
        interfaces = netifaces.interfaces()

        # Priority order: en0 (WiFi), en1 (Ethernet), then others
        priority_interfaces = ['en0', 'en1'] + [i for i in interfaces if i.startswith('en')]

        for interface in priority_interfaces:
            try:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    ip = addrs[netifaces.AF_INET][0]['addr']
                    # Skip localhost and VPN tunnel IPs (10.x.x.x with /16 netmask)
                    if ip != '127.0.0.1' and not ip.startswith('169.254'):
                        # Prefer 192.168.x.x over 10.x.x.x
                        if ip.startswith('192.168') or ip.startswith('172.'):
                            return ip
                        # Store 10.x IP as fallback but keep looking
                        elif ip.startswith('10.'):
                            fallback_ip = ip
            except (KeyError, IndexError):
                continue

        # If we found a 10.x IP but no 192.168.x IP, use it
        if 'fallback_ip' in locals():
            return fallback_ip

        # Fallback to socket method
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"


def generate_qr_code(url):
    """Generate QR code for mobile access."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    # Convert to base64 for embedding in HTML
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"


def get_serializable_state():
    """Get recording state without non-serializable objects."""
    return {
        'active': recording_state['active'],
        'mode': recording_state['mode'],
        'paused': recording_state['paused'],
        'duration': recording_state['duration'],
        'segments': recording_state['segments'],
        'status': recording_state['status']
    }


# Routes
@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/config')
def get_config():
    """Get current configuration."""
    return jsonify({
        'whisper_model': config.whisper_model,
        'sample_rate': config.sample_rate,
        'channels': config.channels,
        'has_api_key': bool(config.anthropic_api_key)
    })


@app.route('/api/status')
def get_status():
    """Get current recording status."""
    return jsonify(get_serializable_state())


@app.route('/api/devices')
def list_devices():
    """List available audio devices."""
    import sounddevice as sd
    devices = sd.query_devices()
    device_list = []
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            device_list.append({
                'id': i,
                'name': device['name'],
                'channels': device['max_input_channels']
            })
    return jsonify(device_list)


@app.route('/api/qrcode')
def get_qrcode():
    """Generate QR code for mobile access."""
    local_ip = get_local_ip()
    port = request.host.split(':')[-1] if ':' in request.host else '5000'
    url = f"http://{local_ip}:{port}"
    qr_image = generate_qr_code(url)
    return jsonify({'qr_code': qr_image, 'url': url})


@app.route('/api/transcripts')
def list_transcripts():
    """List recent transcripts."""
    output_dir = Path('output')
    if not output_dir.exists():
        return jsonify([])

    transcripts = []
    for file in sorted(output_dir.glob('transcript_*.txt'), reverse=True)[:10]:
        stat = file.stat()
        transcripts.append({
            'filename': file.name,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'path': str(file)
        })
    return jsonify(transcripts)


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download a transcript file."""
    file_path = Path('output') / filename
    if file_path.exists() and file_path.is_file():
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


@app.route('/api/video-apps')
def detect_video_apps():
    """Detect running video conferencing applications."""
    detected = VideoChatDetector.detect_running_apps()
    return jsonify({
        'detected': [{'name': app.name, 'process': app.process_name} for app in detected],
        'count': len(detected),
        'instructions': VideoChatDetector.get_setup_instructions(detected)
    })


@app.route('/api/blackhole-status')
def blackhole_status():
    """Check BlackHole installation status."""
    installed = VideoChatDetector.check_blackhole_installed()
    device_id = VideoChatDetector.get_blackhole_device_id() if installed else None
    return jsonify({
        'installed': installed,
        'device_id': device_id
    })


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"Client connected: {request.sid}")
    emit('status', get_serializable_state())


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f"Client disconnected: {request.sid}")


@socketio.on('start_recording')
def handle_start_recording(data):
    """Start a recording session."""
    global recording_state

    if recording_state['active']:
        emit('error', {'message': 'Recording already in progress'})
        return

    mode = data.get('mode', 'standard')
    options = data.get('options', {})

    recording_state['active'] = True
    recording_state['mode'] = mode
    recording_state['status'] = 'recording'
    recording_state['transcript_chunks'] = []
    recording_state['segments'] = 0
    recording_state['duration'] = 0
    recording_state['options'] = options  # Store options for later access

    socketio.emit('status', get_serializable_state())

    # Start recording in background thread
    thread = threading.Thread(
        target=run_recording,
        args=(mode, options),
        daemon=True
    )
    thread.start()

    socketio.emit('recording_started', {'mode': mode})


@socketio.on('pause_recording')
def handle_pause():
    """Pause recording (pausable mode only)."""
    if recording_state['mode'] == 'pausable' and recording_state['audio_capture']:
        # Check if the capture object has pause method (not available in dual-stream mode)
        if hasattr(recording_state['audio_capture'], 'pause'):
            recording_state['audio_capture'].pause()
            recording_state['paused'] = True
            recording_state['status'] = 'paused'
            socketio.emit('status', get_serializable_state())
        else:
            socketio.emit('error', {'message': 'Pause not supported in video conference mode'})


@socketio.on('resume_recording')
def handle_resume():
    """Resume recording (pausable mode only)."""
    if recording_state['mode'] == 'pausable' and recording_state['audio_capture']:
        # Check if the capture object has resume method (not available in dual-stream mode)
        if hasattr(recording_state['audio_capture'], 'resume'):
            recording_state['audio_capture'].resume()
            recording_state['paused'] = False
            recording_state['status'] = 'recording'
            socketio.emit('status', get_serializable_state())
        else:
            socketio.emit('error', {'message': 'Resume not supported in video conference mode'})


@socketio.on('stop_recording')
def handle_stop():
    """Stop recording."""
    if recording_state['active'] and recording_state['status'] != 'stopping':
        # Set status to stopping - recording thread will handle cleanup
        recording_state['status'] = 'stopping'
        socketio.emit('status', get_serializable_state())
        socketio.emit('log', {'message': 'Stopping recording...'})


@socketio.on('update_options')
def handle_update_options(data):
    """Update recording options during active recording."""
    if recording_state['active']:
        new_options = data.get('options', {})
        recording_state['options'].update(new_options)
        socketio.emit('log', {'message': f'Options updated: {list(new_options.keys())}'})
        socketio.emit('options_updated', {'options': recording_state['options']})


@socketio.on('ui_change')
def handle_ui_change(data):
    """Broadcast UI changes to all other clients."""
    # Broadcast to all clients except sender
    emit('ui_sync', data, broadcast=True, include_self=False)


def run_recording(mode, options):
    """Run recording in background thread."""
    global recording_state

    try:
        # Check if video conferencing mode is enabled
        if options.get('video_conference_mode', False):
            # Video conference mode only supports standard and streaming (not pausable)
            if mode == 'pausable':
                socketio.emit('log', {'message': 'Note: Pausable mode not available in video conference. Using standard mode.'})
                run_video_conference_recording(options)
            elif mode == 'streaming':
                run_video_streaming_recording(options)
            else:
                run_video_conference_recording(options)
        elif mode == 'streaming':
            run_streaming_recording(options)
        elif mode == 'pausable':
            run_pausable_recording_session(options)
        else:
            run_standard_recording(options)
    except Exception as e:
        socketio.emit('error', {'message': str(e)})
    finally:
        recording_state['active'] = False
        recording_state['audio_capture'] = None
        recording_state['status'] = 'idle'
        socketio.emit('status', get_serializable_state())


def run_standard_recording(options):
    """Run standard recording mode."""
    global recording_state

    socketio.emit('log', {'message': 'Starting standard recording...'})

    # Create audio capture
    capture = AudioCapture(
        sample_rate=config.sample_rate,
        channels=config.channels
    )
    recording_state['audio_capture'] = capture

    # Start recording
    capture.start_recording()
    socketio.emit('log', {'message': 'Recording... Click Stop when finished'})

    # Wait for stop signal
    while recording_state['status'] != 'stopping':
        socketio.sleep(0.1)

    # Stop and get audio
    audio_data = capture.stop_recording()

    if len(audio_data) > 0:
        recording_state['duration'] = len(audio_data) / config.sample_rate

        # Transcribe
        language = recording_state['options'].get('language')
        lang_msg = f"Transcribing audio ({language if language else 'auto-detect'})..."
        socketio.emit('log', {'message': lang_msg})
        transcriber = WhisperTranscriber(model_name=options.get('model', config.whisper_model))
        result = transcriber.transcribe_array(audio_data, config.sample_rate, language=language)

        transcript_text = result.get('text', '').strip()
        socketio.emit('transcript_chunk', {'text': transcript_text, 'final': True})

        # Claude analysis if full report is enabled (check current options, not initial)
        analysis_file = None
        analysis_content = None
        if recording_state['options'].get('full_report', False) and config.anthropic_api_key:
            socketio.emit('log', {'message': 'Analyzing transcript with Claude...'})
            try:
                analyzer = ClaudeAnalyzer(api_key=config.anthropic_api_key)
                analysis = analyzer.analyze_transcript(transcript_text)
                analysis_content = analysis  # Store the analysis text

                exporter = TranscriptExporter()
                analysis_file = exporter.save_analysis(analysis)
                socketio.emit('log', {'message': f'Analysis saved: {analysis_file}'})
            except Exception as e:
                socketio.emit('log', {'message': f'Analysis failed: {str(e)}'})

        # Save audio if enabled (check current options, not initial)
        audio_file = None
        if recording_state['options'].get('save_audio', False):
            socketio.emit('log', {'message': 'Saving audio file...'})
            audio_file = capture.save_audio(audio_data)
            socketio.emit('log', {'message': f'Audio saved: {audio_file}'})

        # Save transcript
        exporter = TranscriptExporter()
        transcript_file = exporter.save_transcript(transcript_text)

        files = {'transcript': transcript_file}
        if analysis_file:
            files['analysis'] = analysis_file
        if audio_file:
            files['audio'] = audio_file

        socketio.emit('log', {'message': f'Transcript saved: {transcript_file}'})
        socketio.emit('recording_complete', {
            'files': files,
            'analysis_content': analysis_content
        })
    else:
        socketio.emit('log', {'message': 'No audio recorded'})


def run_streaming_recording(options):
    """Run streaming recording mode."""
    global recording_state

    socketio.emit('log', {'message': 'Starting streaming recording...'})

    # Create streaming transcriber
    transcriber = StreamingTranscriber(model_name='tiny')
    transcriber.load_model()

    # Create streaming capture
    capture = StreamingAudioCapture(
        sample_rate=config.sample_rate,
        channels=config.channels,
        chunk_duration=5.0
    )
    recording_state['audio_capture'] = capture

    chunk_counter = [0]

    def streaming_callback(audio_chunk):
        # Only process if still recording
        if not recording_state.get('active') or recording_state.get('status') == 'stopping':
            return

        chunk_counter[0] += 1
        recording_state['segments'] = chunk_counter[0]

        try:
            text = transcriber.stream_transcribe(audio_chunk, chunk_counter[0])
            if text:
                socketio.emit('transcript_chunk', {
                    'text': text,
                    'chunk': chunk_counter[0],
                    'final': False
                })

            socketio.emit('status', get_serializable_state())
        except Exception as e:
            print(f"Error in streaming callback: {e}")
            import traceback
            traceback.print_exc()

    # Start streaming
    capture.start_streaming(streaming_callback)

    # Wait for stop signal
    while recording_state['status'] != 'stopping':
        socketio.sleep(0.1)

    # Stop and finalize
    socketio.emit('log', {'message': 'Stopping audio capture...'})
    print("Calling stop_streaming()...")
    audio_data = capture.stop_streaming()
    print(f"Audio data received: {len(audio_data) if len(audio_data) > 0 else 0} samples")

    # Get complete transcript
    socketio.emit('log', {'message': 'Finalizing transcript...'})
    print("Getting full transcript...")
    full_transcript = transcriber.get_full_transcript()
    print(f"Transcript length: {len(full_transcript)} chars")

    # If transcript is empty, skip analysis and save
    if not full_transcript or len(full_transcript.strip()) == 0:
        socketio.emit('log', {'message': 'No transcript generated'})
        print("No transcript to save")
        return

    # Claude analysis if full report is enabled
    analysis_file = None
    analysis_content = None
    if options.get('full_report', False) and config.anthropic_api_key:
        socketio.emit('log', {'message': 'Analyzing transcript with Claude...'})
        try:
            analyzer = ClaudeAnalyzer(api_key=config.anthropic_api_key)
            analysis = analyzer.analyze_transcript(full_transcript)
            analysis_content = analysis  # Store the analysis text

            exporter = TranscriptExporter()
            analysis_file = exporter.save_analysis(analysis)
            socketio.emit('log', {'message': f'Analysis saved: {analysis_file}'})
        except Exception as e:
            socketio.emit('log', {'message': f'Analysis failed: {str(e)}'})

    # Save audio if enabled (check current options, not initial)
    audio_file = None
    if recording_state['options'].get('save_audio', False) and len(audio_data) > 0:
        socketio.emit('log', {'message': 'Saving audio file...'})
        audio_file = capture.save_audio(audio_data)
        socketio.emit('log', {'message': f'Audio saved: {audio_file}'})

    # Save transcript
    exporter = TranscriptExporter()
    transcript_file = exporter.save_transcript(full_transcript)

    files = {'transcript': transcript_file}
    if analysis_file:
        files['analysis'] = analysis_file
    if audio_file:
        files['audio'] = audio_file

    socketio.emit('log', {'message': f'Streaming complete: {transcript_file}'})
    socketio.emit('recording_complete', {
        'files': files,
        'analysis_content': analysis_content
    })


def run_pausable_recording_session(options):
    """Run pausable recording mode."""
    global recording_state

    socketio.emit('log', {'message': 'Starting pausable recording...'})

    # Create pausable capture
    capture = PausableAudioCapture(
        sample_rate=config.sample_rate,
        channels=config.channels
    )
    recording_state['audio_capture'] = capture

    # Start recording
    capture.start_recording()

    # Wait for stop signal
    while recording_state['status'] != 'stopping':
        # Update status
        status = capture.get_status()
        recording_state['segments'] = status.get('segments', 0)
        recording_state['duration'] = status.get('duration', 0)
        recording_state['paused'] = status.get('is_paused', False)

        socketio.emit('status', get_serializable_state())
        socketio.sleep(0.5)

    # Stop and get audio
    socketio.emit('log', {'message': 'Processing recording...'})
    try:
        audio_data = capture.stop_recording()
    except Exception as e:
        socketio.emit('log', {'message': f'Error stopping recording: {str(e)}'})
        audio_data = np.array([])

    if len(audio_data) > 0:
        # Transcribe
        language = recording_state['options'].get('language')
        lang_msg = f"Transcribing audio ({language if language else 'auto-detect'})..."
        socketio.emit('log', {'message': lang_msg})
        transcriber = WhisperTranscriber(model_name=options.get('model', config.whisper_model))
        result = transcriber.transcribe_array(audio_data, config.sample_rate, language=language)

        transcript_text = result.get('text', '').strip()
        socketio.emit('transcript_chunk', {'text': transcript_text, 'final': True})

        # Claude analysis if full report is enabled (check current options, not initial)
        analysis_file = None
        analysis_content = None
        if recording_state['options'].get('full_report', False) and config.anthropic_api_key:
            socketio.emit('log', {'message': 'Analyzing transcript with Claude...'})
            try:
                analyzer = ClaudeAnalyzer(api_key=config.anthropic_api_key)
                analysis = analyzer.analyze_transcript(transcript_text)
                analysis_content = analysis  # Store the analysis text

                exporter = TranscriptExporter()
                analysis_file = exporter.save_analysis(analysis)
                socketio.emit('log', {'message': f'Analysis saved: {analysis_file}'})
            except Exception as e:
                socketio.emit('log', {'message': f'Analysis failed: {str(e)}'})

        # Save audio if enabled (check current options, not initial)
        audio_file = None
        if recording_state['options'].get('save_audio', False):
            socketio.emit('log', {'message': 'Saving audio file...'})
            audio_file = capture.save_audio(audio_data)
            socketio.emit('log', {'message': f'Audio saved: {audio_file}'})

        # Save transcript
        exporter = TranscriptExporter()
        transcript_file = exporter.save_transcript(transcript_text)

        files = {'transcript': transcript_file}
        if analysis_file:
            files['analysis'] = analysis_file
        if audio_file:
            files['audio'] = audio_file

        socketio.emit('log', {'message': f'Pausable recording complete: {transcript_file}'})
        socketio.emit('recording_complete', {
            'files': files,
            'analysis_content': analysis_content
        })


def run_video_conference_recording(options):
    """Run video conference recording with dual-stream capture."""
    global recording_state

    socketio.emit('log', {'message': 'Starting video conference recording...'})
    socketio.emit('log', {'message': '📹 Dual-stream mode: Mic + System Audio'})

    # Find devices
    mic_device = options.get('mic_device') or DualStreamCapture.find_default_mic()
    system_device = options.get('system_device') or DualStreamCapture.find_blackhole_device()

    if system_device is None:
        socketio.emit('error', {'message': 'BlackHole not found. Please install BlackHole 2ch.'})
        return

    # Create dual-stream capture
    capture = DualStreamCapture(
        mic_device=mic_device,
        system_device=system_device,
        sample_rate=config.sample_rate,
        channels=config.channels
    )
    recording_state['audio_capture'] = capture

    # Start recording
    capture.start_recording()
    socketio.emit('log', {'message': 'Recording... Click Stop when finished'})

    # Wait for stop signal
    while recording_state['status'] != 'stopping':
        socketio.sleep(0.1)

    # Stop and get audio
    combined_audio, mic_audio, system_audio = capture.stop_recording()

    if len(combined_audio) > 0:
        recording_state['duration'] = len(combined_audio) / config.sample_rate

        # Transcribe combined audio
        language = recording_state['options'].get('language')
        lang_msg = f"Transcribing audio ({language if language else 'auto-detect'})..."
        socketio.emit('log', {'message': lang_msg})
        transcriber = WhisperTranscriber(model_name=options.get('model', config.whisper_model))
        result = transcriber.transcribe_array(combined_audio, config.sample_rate, language=language)

        transcript_text = result.get('text', '').strip()
        socketio.emit('transcript_chunk', {'text': transcript_text, 'final': True})

        # Claude analysis if enabled
        analysis_file = None
        analysis_content = None
        if recording_state['options'].get('full_report', False) and config.anthropic_api_key:
            socketio.emit('log', {'message': 'Analyzing transcript with Claude...'})
            try:
                analyzer = ClaudeAnalyzer(api_key=config.anthropic_api_key)
                analysis = analyzer.analyze_transcript(transcript_text)
                analysis_content = analysis

                exporter = TranscriptExporter()
                analysis_file = exporter.save_analysis(analysis)
                socketio.emit('log', {'message': f'Analysis saved: {analysis_file}'})
            except Exception as e:
                socketio.emit('log', {'message': f'Analysis failed: {str(e)}'})

        # Save audio if enabled
        audio_files = {}
        if recording_state['options'].get('save_audio', False):
            socketio.emit('log', {'message': 'Saving audio files...'})
            saved = capture.save_audio(combined_audio, mic_audio, system_audio)
            audio_files = saved
            socketio.emit('log', {'message': f'Audio saved: {len(saved)} files'})

        # Save transcript
        exporter = TranscriptExporter()
        transcript_file = exporter.save_transcript(transcript_text)

        files = {'transcript': transcript_file}
        if analysis_file:
            files['analysis'] = analysis_file
        if audio_files:
            files['audio'] = audio_files.get('combined')
            files['audio_mic'] = audio_files.get('mic')
            files['audio_system'] = audio_files.get('system')

        socketio.emit('log', {'message': f'Video conference recording complete: {transcript_file}'})
        socketio.emit('recording_complete', {
            'files': files,
            'analysis_content': analysis_content
        })
    else:
        socketio.emit('log', {'message': 'No audio recorded'})


def run_video_streaming_recording(options):
    """Run video conference streaming recording with dual-stream capture."""
    global recording_state

    socketio.emit('log', {'message': 'Starting video conference streaming...'})
    socketio.emit('log', {'message': '📹 Dual-stream mode: Mic + System Audio'})

    # Find devices
    mic_device = options.get('mic_device') or DualStreamCapture.find_default_mic()
    system_device = options.get('system_device') or DualStreamCapture.find_blackhole_device()

    if system_device is None:
        socketio.emit('error', {'message': 'BlackHole not found. Please install BlackHole 2ch.'})
        return

    # Create streaming transcriber
    transcriber = StreamingTranscriber(model_name='tiny')
    transcriber.load_model()

    # Create streaming dual capture
    capture = StreamingDualCapture(
        mic_device=mic_device,
        system_device=system_device,
        sample_rate=config.sample_rate,
        channels=config.channels,
        chunk_duration=5.0
    )
    recording_state['audio_capture'] = capture

    chunk_counter = [0]

    def streaming_callback(audio_chunk):
        # Only process if still recording
        if not recording_state.get('active') or recording_state.get('status') == 'stopping':
            return

        chunk_counter[0] += 1
        recording_state['segments'] = chunk_counter[0]

        try:
            text = transcriber.stream_transcribe(audio_chunk, chunk_counter[0])
            if text:
                socketio.emit('transcript_chunk', {
                    'text': text,
                    'chunk': chunk_counter[0],
                    'final': False
                })

            socketio.emit('status', get_serializable_state())
        except Exception as e:
            print(f"Error in streaming callback: {e}")
            import traceback
            traceback.print_exc()

    # Start streaming
    capture.start_streaming(streaming_callback)

    # Wait for stop signal
    while recording_state['status'] != 'stopping':
        socketio.sleep(0.1)

    # Stop and finalize
    socketio.emit('log', {'message': 'Stopping dual-stream capture...'})
    combined_audio, mic_audio, system_audio = capture.stop_streaming()

    # Get complete transcript
    socketio.emit('log', {'message': 'Finalizing transcript...'})
    full_transcript = transcriber.get_full_transcript()

    if not full_transcript or len(full_transcript.strip()) == 0:
        socketio.emit('log', {'message': 'No transcript generated'})
        return

    # Emit the complete transcript to the client
    socketio.emit('transcript_chunk', {'text': full_transcript, 'final': True})

    # Claude analysis if enabled
    analysis_file = None
    analysis_content = None
    if recording_state['options'].get('full_report', False) and config.anthropic_api_key:
        socketio.emit('log', {'message': 'Analyzing transcript with Claude...'})
        try:
            analyzer = ClaudeAnalyzer(api_key=config.anthropic_api_key)
            analysis = analyzer.analyze_transcript(full_transcript)
            analysis_content = analysis

            exporter = TranscriptExporter()
            analysis_file = exporter.save_analysis(analysis)
            socketio.emit('log', {'message': f'Analysis saved: {analysis_file}'})
        except Exception as e:
            socketio.emit('log', {'message': f'Analysis failed: {str(e)}'})

    # Save audio if enabled
    audio_files = {}
    if recording_state['options'].get('save_audio', False) and len(combined_audio) > 0:
        socketio.emit('log', {'message': 'Saving audio files...'})
        saved = capture.save_audio(combined_audio, mic_audio, system_audio)
        audio_files = saved
        socketio.emit('log', {'message': f'Audio saved: {len(saved)} files'})

    # Save transcript
    exporter = TranscriptExporter()
    transcript_file = exporter.save_transcript(full_transcript)

    files = {'transcript': transcript_file}
    if analysis_file:
        files['analysis'] = analysis_file
    if audio_files:
        files['audio'] = audio_files.get('combined')

    socketio.emit('log', {'message': f'Video conference streaming complete: {transcript_file}'})
    socketio.emit('recording_complete', {
        'files': files,
        'analysis_content': analysis_content
    })


def print_startup_info(host, port):
    """Print startup information with QR code."""
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{port}"

    print("\n" + "="*60)
    print("🌐 CallScribe Web Interface")
    print("="*60)
    print(f"\n✓ Server running at:")
    print(f"  - Local:   http://localhost:{port}")
    print(f"  - Network: {local_url}")
    print(f"\n📱 Mobile Access:")
    print(f"  Scan the QR code in the web interface")
    print(f"  or visit: {local_url}")

    # Add video conferencing detection
    detected_apps = VideoChatDetector.detect_running_apps()
    if detected_apps:
        print(f"\n📹 Video Conference Apps Detected: {', '.join([app.name for app in detected_apps])}")

    blackhole_installed = VideoChatDetector.check_blackhole_installed()
    if blackhole_installed:
        print("✓ BlackHole installed")
    else:
        print("⚠️  BlackHole not found (needed for video conferencing)")

    print("\n" + "="*60 + "\n")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    global recording_state
    print("\n\n🛑 Shutting down server...")

    # Stop any active recording
    if recording_state.get('active'):
        print("   Stopping active recording...")
        recording_state['status'] = 'stopping'
        recording_state['active'] = False

    print("   Server stopped.")
    sys.exit(0)


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask-SocketIO server."""
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print_startup_info(host, port)

    try:
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)


if __name__ == '__main__':
    run_server()
