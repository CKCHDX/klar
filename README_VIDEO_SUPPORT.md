# Klar Video Support Module

Enhanced video detection, platform identification, and player generation for the Klar Swedish search browser.

## Features

### Supported Platforms

- **YouTube** - Full embed support with controls
- **Vimeo** - Premium player with quality selection
- **Dailymotion** - Fast streaming with adaptive bitrate
- **Twitch** - Live streams and VOD playback
- **TikTok** - Short-form video embeds
- **Instagram** - Photo/video posts
- **HTML5 Direct** - MP4, WebM, OGV, HLS, DASH

### Detection Methods

#### Platform Detection
Automatic detection of video URLs using regex patterns:
- Domain-based detection (youtube.com, vimeo.com, etc.)
- Short URL detection (youtu.be, dai.ly, etc.)
- Video ID extraction for embeds

#### Direct File Detection
Automatic detection of direct video file URLs:
- `.mp4` - MPEG-4 video (H.264 codec)
- `.webm` - WebM format (VP8/VP9 codec)
- `.ogv` - Ogg Theora video
- `.m3u8` - HTTP Live Streaming (HLS)
- `.mpd` - Dynamic Adaptive Streaming (DASH)

## Architecture

### Components

#### 1. `VideoType` Enum
Enumeration of supported video types:
```python
class VideoType(Enum):
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    TWITCH = "twitch"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    HTML5_MP4 = "mp4"
    HTML5_WEBM = "webm"
    HTML5_OGV = "ogv"
    HLS_STREAM = "hls"
    DASH_STREAM = "dash"
    UNKNOWN = "unknown"
```

#### 2. `VideoDetector` Class
Detects video content from URLs using regex patterns:

```python
# Basic usage
is_video, video_type, video_id = VideoDetector.detect_from_url(url)

# Returns:
# - is_video: bool - Whether URL contains video
# - video_type: VideoType - Platform/format type
# - video_id: str|None - Extracted video ID (if applicable)
```

**Detection Patterns:**
- YouTube: `youtube.com/watch?v=`, `youtu.be/`, `youtube.com/embed/`
- Vimeo: `vimeo.com/`, `player.vimeo.com/video/`
- Dailymotion: `dailymotion.com/video/`, `dai.ly/`
- Twitch: `twitch.tv/`, `twitch.tv/videos/`
- TikTok: `tiktok.com/*/video/`
- Instagram: `instagram.com/p/`, `instagram.com/reel/`

#### 3. `VideoMetadata` Class
Extracts and manages video information:

```python
metadata = VideoMetadata(url)
print(metadata.title)        # Extracted or generated title
print(metadata.video_type)   # Detected platform type
print(metadata.video_id)     # Extracted video ID
print(metadata.is_embeddable())  # Can use embed HTML
print(metadata.is_playable_html5())  # Can use HTML5 player
```

**Title Extraction Priority:**
1. From URL query parameters (title=...)
2. From filename (removes extension, replaces dashes/underscores)
3. From domain (e.g., "Video from youtube")

#### 4. `VideoPlayer` Class
Generates HTML for video playback with two strategies:

##### Embedded Player (Platform-Specific)

For services with official embed support:

```python
html = VideoPlayer.generate_embed_html(
    url=url,
    video_type=video_type,
    video_id=video_id,
    width=900,
    height=506
)
```

**Platform-Specific Implementation:**
- **YouTube**: Uses official iframe with parameters (rel=0 for no recommendations)
- **Vimeo**: Premium player with full controls
- **Dailymotion**: Adaptive bitrate streaming
- **Twitch**: Chat integration support
- **TikTok**: Blockquote embed with async script loading
- **Instagram**: Blockquote embed with native embed.js

##### HTML5 Player (Direct Files)

For direct video file URLs:

```python
html = VideoPlayer.generate_html5_player(
    url=url,
    video_type=video_type,
    title="My Video"
)
```

**Features:**
- Responsive 16:9 aspect ratio
- Native HTML5 `<video>` controls
- Keyboard shortcuts:
  - **Space** - Play/Pause
  - **→** - Forward 5 seconds
  - **←** - Rewind 5 seconds
  - **f** - Fullscreen
  - **m** - Mute
  - **↑/↓** - Volume control
  - **> / .** - Speed up
  - **< / ,** - Speed down
- MIME type detection (mp4, webm, ogg, hls)
- Modern dark theme matching Klar design
- Keyboard controls documentation in UI

## Integration with Klar Browser

### In `klar_browser.py`

#### Imports
```python
from engine.video_support import VideoDetector, VideoPlayer, VideoMetadata, VideoType
```

#### Enhanced URL Checking
```python
def check_video_url(self, qurl: QUrl):
    """Enhanced video detection and handling"""
    url_string = qurl.toString()
    
    # Detect video
    is_video, video_type, video_id = VideoDetector.detect_from_url(url_string)
    
    if is_video:
        metadata = VideoMetadata(url_string)
        
        # Use embedded player if available
        if metadata.is_embeddable() and video_id:
            embed_html = VideoPlayer.generate_embed_html(
                url_string, video_type, video_id
            )
            # Wrap and display
        
        # Use HTML5 player for direct files
        elif metadata.is_playable_html5():
            player_html = VideoPlayer.generate_html5_player(
                url_string, video_type, metadata.title
            )
            # Display
        
        # Fallback to external browser
        else:
            webbrowser.open(url_string)
```

### Browser Codec Configuration

WebEngine settings in Klar:
```python
profile = QWebEngineProfile.defaultProfile()
settings = profile.settings()

# Enable video playback
settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)

print("[Video] Supported formats: MP4, WebM, OGV, HLS, DASH")
print("[Video] Supported platforms: YouTube, Vimeo, Dailymotion, Twitch, TikTok")
```

## Usage Examples

### Example 1: YouTube Video
```python
url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

is_video, vtype, vid = VideoDetector.detect_from_url(url)
# True, VideoType.YOUTUBE, "dQw4w9WgXcQ"

metadata = VideoMetadata(url)
print(metadata.title)  # "My Video"
print(metadata.is_embeddable())  # True

html = VideoPlayer.generate_embed_html(url, vtype, vid)
# Returns embedded YouTube iframe
```

### Example 2: Direct MP4 File
```python
url = "https://example.com/videos/sample.mp4"

is_video, vtype, vid = VideoDetector.detect_from_url(url)
# True, VideoType.HTML5_MP4, None

metadata = VideoMetadata(url)
print(metadata.is_playable_html5())  # True

html = VideoPlayer.generate_html5_player(url, vtype, "Sample Video")
# Returns HTML5 player with controls
```

### Example 3: HLS Stream
```python
url = "https://example.com/stream/live.m3u8"

is_video, vtype, vid = VideoDetector.detect_from_url(url)
# True, VideoType.HLS_STREAM, None

html = VideoPlayer.generate_html5_player(url, vtype)
# Returns HTML5 player supporting HLS streaming
```

## Performance Considerations

### Detection
- Regex patterns are optimized for performance
- Single-pass detection (no re-scanning)
- Complexity: O(1) per URL

### Player Generation
- HTML generation is string-based (no DOM manipulation)
- Minimal external dependencies
- Self-contained CSS and JavaScript

### Browser Playback
- Native HTML5 video controls (hardware accelerated)
- WebGL support for advanced effects
- No additional plugins required

## Security Considerations

### URL Sanitization
- All user-supplied URLs escaped for HTML context
- Special characters replaced: `"` → `&quot;`
- XSS prevention in title/metadata display

### CORS Handling
- `crossorigin="anonymous"` for HTML5 video
- iframes use platform-provided embed URLs (safe)
- No direct file downloads enabled (`controlsList="nodownload"`)

### Content Isolation
- Video content loaded in separate context
- No access to browser cookies/local storage from embeds
- Iframe sandboxing where applicable

## Compatibility

### Browser Support
- **Chrome/Chromium 90+** - Full support
- **Firefox 88+** - Full support
- **Safari 14+** - Full support (except DASH)
- **Edge 90+** - Full support

### Video Format Support

| Format | Codec | Support | Notes |
|--------|-------|---------|-------|
| MP4 | H.264 | Full | Most compatible |
| WebM | VP8/VP9 | Full | Open format |
| OGV | Theora | Full | Older format |
| HLS | H.264/HEVC | Full | Streaming |
| DASH | H.264/VP9 | Full | Adaptive |

## Troubleshooting

### Video Not Detected
1. Check URL format matches expected pattern
2. Verify domain is in the regex patterns
3. Use URL with explicit video ID

### Playback Issues
- Ensure WebEngine codec support enabled
- Check video URL is publicly accessible
- Verify CORS headers if self-hosted

### Embed Not Displaying
- Confirm platform supports embedding
- Check video_id was extracted correctly
- Verify network connectivity for embed script loading

## Future Enhancements

- [ ] Subtitles/CC support
- [ ] Playlist detection
- [ ] Live stream detection (YouTube Live, Twitch)
- [ ] HDR video support
- [ ] Picture-in-picture mode
- [ ] Video analytics integration
- [ ] Local M3U playlist support
- [ ] AV1 codec support

## Dependencies

- Python 3.7+
- PyQt6 (for browser integration)
- re (standard library)
- urllib.parse (standard library)
- enum (standard library)

## License

Part of Klar Search Engine - Open source
