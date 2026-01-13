# Web GUI Guide

## Overview

CallScribe's Web GUI provides a modern, Apple-inspired browser interface for AI-powered transcription. Access it from your desktop browser or mobile device, with real-time updates, cross-device control, and automatic network detection.

## Quick Start

### Launch Web Interface

```bash
source venv/bin/activate
python -m callscribe gui
```

**What happens:**
1. ✅ Web server starts on `http://localhost:8080`
2. ✅ Browser opens automatically
3. ✅ Local IP address detected automatically (works on any network)
4. ✅ QR code generated for mobile access
5. ✅ Ready to record!

### Alternative Launch Methods

```bash
# Specify custom port
python -m callscribe gui --port 3000

# Don't open browser automatically
python -m callscribe gui --no-browser

# Custom host (for network access)
python -m callscribe gui --host 0.0.0.0

# Debug mode
python -m callscribe gui --debug
```

## Key Features

### 🎨 Modern Apple-Inspired Design
- Clean, minimalist interface with iOS-style elements
- Logo-style header with meeting background
- Compact layout optimized for screen visibility
- Toggle switches and rounded corners
- Professional blue gradient color scheme

### 📱 Cross-Device Support
- **Desktop**: Full-featured interface with all controls
- **Mobile**: Responsive design that adapts to phone screens
- **Tablet**: Optimized layout for medium-sized screens
- **QR Code**: Instant mobile connection by scanning
- **State Sync**: All devices show the same status in real-time

### 🔄 Real-Time Synchronization
- Start recording on desktop, stop on mobile (or vice versa)
- Live status updates across all connected devices
- Duration counter syncs automatically
- Transcript appears simultaneously on all devices
- Button states update based on server state

### 🌐 Network Portability
- **Automatic IP Detection**: Finds your WiFi IP at startup
- **Works Anywhere**: Home, office, coffee shop - no configuration needed
- **Dynamic QR Code**: Updates for current network automatically
- **VPN Aware**: Prioritizes WiFi over VPN connections
- **Fallback Support**: Multiple detection methods for reliability

### 🎙️ Three Recording Modes
- **Standard**: Traditional start/stop recording
- **Streaming**: Real-time transcription every 5 seconds
- **Pausable**: Interactive pause/resume during recording

### 📊 Live Updates
- **Real-Time Transcript**: See text as it's transcribed
- **Status Panel**: Monitor duration, mode, and status
- **Activity Log**: View all system messages with timestamps
- **Analysis Display**: View Claude analysis with formatted output

## Interface Components

### 1. Header Section
- **CALLSCRIBE** logo in uppercase with meeting background
- Professional gradient overlay (blue to purple)
- Visible silhouettes of people in a meeting
- Subtitle: "AI-Powered Call Transcription"

### 2. Status Bar
- **Status**: Idle, Recording, Paused, Stopping
- **Duration**: Real-time counter (MM:SS format)
- **Mode**: Current recording mode (Standard/Streaming/Pausable)
- Animated red gradient when recording

### 3. Recording Mode Selector
Three large, clickable mode buttons:
- **📄 Standard**: Basic recording with start/stop
- **📡 Streaming**: Live transcription as you speak
- **⏯️ Pausable**: Pause and resume capability

### 4. Options Panel (Collapsible)
**Feature Toggles:**
- 🔊 **Speaker Detection**: Identify different speakers
- ⏱️ **Timestamps**: Add time markers to transcript
- 📝 **Full Report**: Generate Claude analysis
- 💾 **Save Audio**: Keep WAV file of recording

**Dropdown Selectors:**
- **Speakers**: 2, 3, 4, or 5 speakers
- **Model**: Tiny, Base, Small, Medium, Large
- **Language**: Auto-detect or choose from 90+ languages

### 5. Control Buttons
- **▶️ Start**: Begin recording (blue button)
- **⏸️ Pause**: Pause recording (gray, pausable mode only)
- **⏹️ Stop**: End recording (red button)

Buttons automatically enable/disable based on state.

### 6. Live Transcript Window
- **During Recording**: Shows text as it appears
- **After Recording**: Displays complete transcript
- **With Analysis**: Shows formatted Claude analysis
  - Headings in different sizes
  - Bulleted and numbered lists
  - Bold text for emphasis
  - Proper paragraph spacing

Title changes from "Live Transcript" to "Analysis" when displaying Claude output.

### 7. Activity Log
- Timestamped system messages
- Connection status
- Processing updates
- File save confirmations
- Error messages (if any)
- Scrollable with auto-scroll to latest

### 8. Mobile Access Section
- **QR Code**: Scan with phone camera
- **URL Display**: Shows current network IP
- Updates automatically for current network

## Desktop Workflow

### Basic Recording Session

1. **Launch Application**
   ```bash
   python -m callscribe gui
   ```

2. **Configure Options**
   - Click "▼ Options" to expand panel
   - Toggle desired features (Speaker Detection, Timestamps, Full Report)
   - Select Whisper model (Base recommended)
   - Choose language or leave as Auto-detect

3. **Select Recording Mode**
   - Click one of the three mode buttons
   - Standard: Simple start/stop
   - Streaming: Real-time transcription
   - Pausable: Can pause during recording

4. **Start Recording**
   - Click **▶️ Start** button
   - Status changes to "Recording"
   - Duration counter begins
   - Transcript appears in real-time (streaming mode)

5. **Monitor Progress**
   - Watch live transcript window
   - Check activity log for status updates
   - Duration counter shows elapsed time

6. **Stop Recording**
   - Click **⏹️ Stop** button
   - Status changes to "Stopping"
   - Transcription begins
   - Analysis runs (if enabled)

7. **View Results**
   - Complete transcript displays in window
   - If Full Report enabled, analysis replaces transcript
   - Analysis shows formatted output with headings, lists
   - Files saved to `output/` directory

## Mobile Workflow

### Connecting Mobile Device

**Method 1: QR Code (Easiest)**
1. Open Camera app on your phone
2. Point at QR code on desktop screen
3. Tap notification to open link
4. Mobile interface loads automatically

**Method 2: Manual URL**
1. Note the IP address displayed (e.g., `http://192.168.1.230:8080`)
2. Open mobile browser
3. Type or paste the URL
4. Mobile interface loads

**Requirements:**
- Both devices on same WiFi network
- Firewall allows port 8080
- URL uses IP address shown on screen (not localhost)

### Using Mobile Interface

1. **View Status**
   - All information visible on mobile
   - Status, duration, mode display at top
   - Compact layout fits mobile screens

2. **Control Recording**
   - Tap mode buttons to switch modes
   - Tap ▶️ Start to begin (syncs to desktop)
   - Tap ⏹️ Stop to end (syncs to desktop)
   - Pause button available in pausable mode

3. **Monitor Progress**
   - Live transcript scrolls automatically
   - Activity log shows system messages
   - All updates appear instantly

4. **Cross-Device Control**
   - Start on mobile, stop on desktop
   - Start on desktop, stop on mobile
   - All devices see same state
   - Buttons enable/disable together

## Recording Modes Explained

### Standard Mode
**Best for**: Simple meetings, quick recordings

**How it works:**
- Click Start to begin
- Click Stop to end
- Transcription happens after recording
- Analysis runs after transcription

**Advantages:**
- Simple and straightforward
- Most reliable
- Works with any audio length

### Streaming Mode
**Best for**: Long meetings where you want to see text immediately

**How it works:**
- Transcription happens every 5 seconds
- See words appear as you speak
- Complete transcript compiled at end
- Analysis runs on full transcript

**Advantages:**
- Real-time feedback
- Know immediately if audio is working
- Can read along during meeting

**Note:** May show chunks out of order if speech is fast

### Pausable Mode
**Best for**: Interviews, multi-part recordings

**How it works:**
- Click Pause to temporarily stop
- Click Resume to continue
- Audio segments combined at end
- Transcription after final stop

**Advantages:**
- Skip breaks or off-topic discussion
- Control exactly what gets recorded
- Duration tracks active recording time

## Language Support

CallScribe supports 90+ languages with automatic detection:

### Auto-Detection (Recommended)
- Whisper identifies the language automatically
- Works for any supported language
- Select "Auto-detect" in Language dropdown

### Manual Selection
Available languages include:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Dutch (nl)
- Russian (ru)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- And 80+ more...

### Using Language Selection

**In Web GUI:**
1. Expand Options panel
2. Click Language dropdown
3. Select "Auto-detect" or specific language
4. Start recording

**CLI:**
```bash
# Auto-detect
python -m callscribe.main --language auto

# Specific language
python -m callscribe.main --language es
```

## Analysis Display

When "Full Report" is enabled, Claude analyzes your transcript and the results appear directly in the browser.

### Features
- **Formatted Output**: Headings, lists, and emphasis
- **Professional Layout**: Clean, readable typography
- **Automatic Display**: Replaces transcript when ready
- **Markdown Support**: Converts markdown to styled HTML

### Analysis Elements
- **H1 Headings**: Main sections (18px, blue)
- **H2 Headings**: Subsections (16px)
- **H3 Headings**: Details (14px)
- **Bullet Lists**: Key points
- **Numbered Lists**: Sequential items
- **Bold Text**: Important information
- **Paragraphs**: Formatted with proper spacing

### Example Analysis Structure
```
# Meeting Summary

## Key Discussion Points
- Project timeline approved
- Budget considerations discussed
- Next steps identified

## Action Items
1. Complete design review by Friday
2. Schedule follow-up meeting
3. Distribute meeting notes

## Recommendations
Focus on the high-priority items first...
```

## Network Configuration

### How IP Detection Works

1. **At Startup**: Server calls `get_local_ip()` function
2. **Priority Order**:
   - WiFi interface (en0)
   - Ethernet (en1)
   - Other network interfaces
3. **Filtering**:
   - Skips localhost (127.0.0.1)
   - Avoids VPN tunnels (10.x.x.x with /16 netmask)
   - Prefers 192.168.x.x over 10.x.x.x
4. **Fallback**: Uses socket connection test if needed
5. **Display**: Shows detected IP in terminal and QR code

### Supported Network Types
- ✅ Home WiFi (192.168.x.x)
- ✅ Office Networks (10.x.x.x, 172.16.x.x)
- ✅ Public WiFi (various ranges)
- ✅ Mobile Hotspots
- ⚠️ VPN tunnels (detected but lower priority)

### Portability
The IP is detected fresh each time you run the application:
- **Your Network**: Detects your IP
- **Friend's Network**: Detects their IP
- **Coffee Shop**: Detects public WiFi IP
- **No configuration needed**

## Technical Details

### WebSocket Communication
- **Protocol**: Socket.IO over WebSocket
- **Events**: Bidirectional real-time messaging
- **Reliability**: Automatic reconnection
- **Broadcasting**: Updates sent to all connected clients

### State Synchronization
Server maintains single source of truth:
- `recording_state` dictionary tracks current state
- All clients receive same status updates
- Button states derived from server state
- Duration synced from server in pausable mode

### Event Types
- `connect`: Client connects to server
- `disconnect`: Client disconnects
- `start_recording`: Begin recording
- `stop_recording`: End recording
- `pause_recording`: Pause (pausable mode)
- `resume_recording`: Resume (pausable mode)
- `recording_started`: Broadcast recording began
- `recording_complete`: Broadcast recording finished
- `transcript_chunk`: Real-time transcript segment
- `status`: Status update broadcast
- `log`: Activity log message
- `update_options`: Change options during recording
- `ui_change`: Sync UI changes across devices

## Troubleshooting

### Mobile Can't Connect

**Problem**: QR code doesn't work or URL won't load

**Solutions:**
1. Verify both devices on same WiFi network
2. Check firewall allows port 8080
3. Try manual URL entry instead of QR code
4. Ensure URL uses IP address (not localhost)
5. Restart server to refresh IP detection

### State Not Syncing

**Problem**: Mobile shows different status than desktop

**Solutions:**
1. Refresh browser page
2. Check console for errors (F12)
3. Verify WebSocket connection in Activity Log
4. Restart server if persistent

### Duration Counter Issues

**Problem**: Duration not updating or jumping

**Solutions:**
1. Ensure pausable mode gets duration from server
2. Standard/streaming use local timer
3. Timer resets on new recording
4. Check for JavaScript errors in console

### Recording Won't Stop

**Problem**: Stop button clicked but recording continues

**Solutions:**
1. Fixed in latest version
2. Check terminal for "Stopping streaming..." message
3. Look for thread/callback errors
4. Use Ctrl+C to force shutdown if needed

### Analysis Not Displaying

**Problem**: Full Report enabled but analysis doesn't appear

**Solutions:**
1. Verify Claude API key in `.env` file
2. Check Activity Log for analysis messages
3. Wait for "Analysis saved" log entry
4. Refresh browser if analysis completed

### Compact UI Too Small

**Problem**: Text or elements too small to read

**Solutions:**
1. Use browser zoom (Cmd/Ctrl +)
2. Adjust browser's default font size
3. Use larger display if available
4. Elements sized for 1920x1080 minimum

## Advanced Usage

### Custom Port
```bash
python -m callscribe gui --port 3000
# Access at http://localhost:3000
```

### Network Access
```bash
python -m callscribe gui --host 0.0.0.0
# Accessible from any device on network
```

### Debug Mode
```bash
python -m callscribe gui --debug
# Shows detailed Flask/SocketIO logs
```

### Multiple Sessions
- Only one recording can be active at a time
- Multiple clients can connect and view
- Control available on all connected devices
- Last client to connect sees current state

## Best Practices

### For Meetings
1. Test audio before important meeting
2. Use Standard mode for reliability
3. Enable Full Report for insights
4. Save audio for archival purposes

### For Interviews
1. Use Pausable mode for breaks
2. Enable Speaker Detection
3. Include timestamps for reference
4. Review transcript before sharing

### For Demos
1. Use mobile control for flexibility
2. Position QR code for easy scanning
3. Test connection before presenting
4. Have backup (CLI mode) ready

### For Development
1. Use Debug mode to see all events
2. Monitor terminal for backend logs
3. Check browser console for errors
4. Test on actual devices, not just emulators

## File Output

All files saved to `output/` directory:

### Transcript Files
- **Filename**: `transcript_YYYYMMDD_HHMMSS.txt`
- **Content**: Raw transcript text
- **Format**: Plain text or Markdown

### Analysis Files
- **Filename**: `analysis_YYYYMMDD_HHMMSS.md`
- **Content**: Claude's analysis
- **Format**: Markdown with formatting

### Audio Files (if enabled)
- **Filename**: `recording_YYYYMMDD_HHMMSS.wav`
- **Content**: Recorded audio
- **Format**: 16-bit PCM WAV, 16kHz

## Security Considerations

### Network Security
- Server binds to localhost by default
- Mobile access requires same network
- No authentication required (local network)
- Consider firewall rules for public networks

### Data Privacy
- All transcription happens locally (Whisper)
- Only transcript sent to Claude API
- Audio files stored locally
- Delete recordings when no longer needed

### API Keys
- Store in `.env` file (not committed to git)
- Never share API keys
- Rotate keys periodically
- Monitor API usage

## Performance Tips

### For Better Speed
- Use smaller Whisper model (tiny, base)
- Disable speaker diarization if not needed
- Skip Claude analysis for quick transcripts
- Close other resource-intensive apps

### For Better Accuracy
- Use larger Whisper model (medium, large)
- Select correct language manually
- Ensure good audio quality
- Minimize background noise

### For Long Recordings
- Standard mode recommended
- Streaming may have memory overhead
- Pausable mode for breaks
- Monitor system resources

## Updates and Maintenance

### Checking for Updates
```bash
cd call_transcription
git pull origin main
pip install -r requirements.txt --upgrade
```

### Backup Recommendations
- Back up `.env` file (contains API key)
- Archive important transcripts
- Save audio files if needed for compliance
- Export analysis to external storage

## Support

For issues or questions:
1. Check this guide first
2. Review terminal logs for errors
3. Check browser console (F12) for JavaScript errors
4. Refer to other documentation files
5. Check requirements.txt for dependency issues

## Related Documentation

- **[README.md](README.md)** - Main project overview
- **[STREAMING_GUIDE.md](STREAMING_GUIDE.md)** - Streaming mode details
- **[PAUSABLE_GUIDE.md](PAUSABLE_GUIDE.md)** - Pausable mode details
- **[SPEAKER_DIARIZATION_GUIDE.md](SPEAKER_DIARIZATION_GUIDE.md)** - Speaker detection
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
