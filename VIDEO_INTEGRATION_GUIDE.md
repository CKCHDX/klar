# Video Support Integration Guide

## Overview

This guide explains how to integrate the new `video_support.py` module into Klar 3.1 for enhanced video playback capabilities.

## Current Status

**Video playback is already enabled** in `klar_browser.py` with these features:

- ✅ HTML5 video codec support
- ✅ Plugin support enabled
- ✅ JavaScript video controls enabled
- ✅ Autoplay without user gesture
- ✅ Direct video file detection and playback
- ✅ Streaming platform support (YouTube, Vimeo, etc.)

## New Module: `engine/video_support.py`

### Features

1. **VideoDetector Class**
   - Detects video URLs and file types
   - Identifies streaming platforms
   - Extracts video IDs from URLs
   - Determines playback method

2. **VideoPlayer Class**
   - Generates HTML5 player HTML
   - Creates platform-specific embeds
   - Handles player initialization

3. **VideoMetadata Class**
   - Extracts video information
   - Determines best playback method
   - Provides metadata dictionary

### Installation

The module is already added to your repository at:
```
engine/video_support.py
```

## Integration with klar_browser.py

### Step 1: Import the Module

Add to the imports section at the top of `klar_browser.py` (after line 25):

```python
from engine.video_support import VideoDetector, VideoPlayer, VideoMetadata
```

### Step 2: Enhanced Video Detection

Replace the `check_video_url()` method (around line 380) with:

```python
def check_video_url(self, qurl: QUrl):
    """Enhanced video detection and handling"""
    url_string = qurl.toString()
    
    # Use new video detector
    is_video, video_type, video_id = VideoDetector.detect_from_url(url_string)
    
    if is_video:
        print(f"[Video] Detected: {video_type}")
        
        # Create metadata
        metadata = VideoMetadata(url_string)
        print(f"[Video] Metadata: {metadata.to_dict()}")
        
        # Handle embeddable platforms
        if metadata.is_embeddable():
            print(f"[Video] Using embedded player for {video_type}")
            embed_html = VideoPlayer.generate_embed_html(
                url_string, video_type, video_id
            )
            if embed_html:
                # Wrap in styled container
                html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0; padding: 20px;
            background: #0a0e1a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .video-container {{
            width: 100%;
            max-width: 900px;
        }}
    </style>
</head>
<body>
    <div class="video-container">
        {embed_html}
    </div>
</body>
</html>'''
                self.current_browser().setHtml(html, QUrl("about:blank"))
                self.status.showMessage(f"▶ Playing {metadata.title}", 3000)
                return
        
        # Handle direct playback
        elif metadata.is_playable_html5():
            print(f"[Video] Using HTML5 player for {video_type}")
            player_html = VideoPlayer.generate_html5_player(
                url_string, video_type, metadata.title
            )
            if player_html:
                self.current_browser().setHtml(player_html, QUrl("about:blank"))
                self.status.showMessage(f"▶ Playing {metadata.title}", 3000)
                return
        
        # Fallback: open externally
        print(f"[Video] Opening externally: {url_string}")
        webbrowser.open(url_string)
        self.current_browser().back()
```

### Step 3: Add Video Information Display

Add this method to the KlarBrowser class:

```python
def display_video_info(self, metadata: VideoMetadata):
    """Display video information in status bar"""
    info_parts = []
    info_parts.append(f"📹 {metadata.title}")
    
    if metadata.video_type:
        info_parts.append(f"Type: {metadata.video_type.name}")
    
    if metadata.video_id:
        info_parts.append(f"ID: {metadata.video_id}")
    
    info_message = " | ".join(info_parts)
    self.status.showMessage(info_message, 5000)
```

### Step 4: Cache Video Metadata (with LOKI)

Add to `_cache_page_content()` method:

```python
def _cache_video_metadata(self, url: str, metadata: VideoMetadata):
    """Cache video metadata if LOKI enabled"""
    if self.loki and self.loki.settings.get('enabled', False):
        try:
            self.loki.cache_page({
                'url': url,
                'title': metadata.title,
                'type': 'video',
                'metadata': metadata.to_dict(),
                'content': metadata.title
            })
            print(f"[LOKI] Cached video: {metadata.title}")
        except Exception as e:
            print(f"[LOKI] Video cache error: {e}")
```

## Usage Examples

### Example 1: Direct Detection

```python
from engine.video_support import VideoDetector, VideoMetadata

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
is_video, video_type, video_id = VideoDetector.detect_from_url(url)

if is_video:
    metadata = VideoMetadata(url)
    print(metadata.to_dict())
    # Output: {
    #   'is_video': True,
    #   'type': 'YOUTUBE',
    #   'video_id': 'dQw4w9WgXcQ',
    #   'title': 'YouTube Video',
    #   'is_embeddable': True
    # }
```

### Example 2: Generate Player

```python
from engine.video_support import VideoPlayer, VideoType

url = "https://example.com/video.mp4"
html = VideoPlayer.generate_html5_player(
    url,
    VideoType.MP4,
    title="My Video"
)

browser.setHtml(html)
```

### Example 3: Get Embed Code

```python
from engine.video_support import VideoDetector, VideoPlayer

url = "https://vimeo.com/123456789"
is_video, video_type, video_id = VideoDetector.detect_from_url(url)

if is_video and video_id:
    embed_html = VideoPlayer.generate_embed_html(
        url, video_type, video_id, width=800, height=450
    )
    print(embed_html)
```

## Supported Formats

### Video Containers
- MP4 (.mp4, .m4v)
- WebM (.webm)
- Ogg (.ogv, .ogg)
- QuickTime (.mov)
- Matroska (.mkv)
- AVI (.avi)
- Flash Video (.flv)
- HLS Streaming (.m3u8)
- DASH Streaming (.mpd)

### Streaming Platforms
- YouTube (youtube.com, youtu.be)
- Vimeo (vimeo.com)
- Dailymotion (dailymotion.com)
- Twitch (twitch.tv)
- TikTok (tiktok.com)

## Configuration Options

### Enable/Disable Features

In `klar_browser.py` initialization:

```python
# Allow autoplay without user gesture
settings.setAttribute(
    QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, 
    False
)

# Enable plugins for video
settings.setAttribute(
    QWebEngineSettings.WebAttribute.PluginsEnabled, 
    True
)

# Allow insecure content (for mixed HTTP/HTTPS)
settings.setAttribute(
    QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, 
    True
)
```

## Performance Optimization

### Hardware Acceleration

```python
# Enable WebGL for hardware acceleration
settings.setAttribute(
    QWebEngineSettings.WebAttribute.WebGLEnabled,
    True
)
```

### Caching

```python
# Enable caching for better performance
profile = QWebEngineProfile.defaultProfile()
profile.httpCacheType = QWebEngineProfile.HttpCacheType.DiskHttpCache
profile.cachePath = str(Path.home() / "Klar-cache")
```

## Testing

### Test Script

```python
# Save as test_video_support.py
from engine.video_support import VideoDetector, VideoMetadata

test_urls = [
    "https://www.youtube.com/watch?v=VIDEO_ID",
    "https://vimeo.com/123456789",
    "https://example.com/video.mp4",
    "https://example.com/stream.m3u8",
]

for url in test_urls:
    print(f"\nTesting: {url}")
    metadata = VideoMetadata(url)
    print(f"Is Video: {metadata.is_video}")
    print(f"Type: {metadata.video_type}")
    print(f"Embeddable: {metadata.is_embeddable()}")
    print(f"HTML5: {metadata.is_playable_html5()}")
```

Run with:
```bash
python test_video_support.py
```

## Troubleshooting

### Video Not Detected

1. Check URL format
2. Verify platform is in STREAMING_PLATFORMS
3. Test with `VideoDetector.detect_from_url(url)`

### Player Not Loading

1. Check browser permissions
2. Verify HTML generation succeeded
3. Check console logs for errors

### Playback Issues

1. Check codec support: `VideoDetector.is_streamable_format()`
2. Verify MIME type: `VideoDetector.get_mime_type()`
3. Test alternative format

## Advanced Features

### Custom Platform Support

Add to `VideoDetector.PLATFORMS`:

```python
'custom_platform': {
    'patterns': [
        r'custom\.com\/video\/(\d+)',
    ],
    'video_type': VideoType.YOUTUBE,  # or custom type
    'supports_embed': True,
    'embed_template': 'https://custom.com/embed/{video_id}',
}
```

### Video Quality Selection

```python
# Add to VideoPlayer class
@staticmethod
def generate_adaptive_player(url: str, qualities: List[str]):
    """Generate player with quality selection"""
    # Implementation here
    pass
```

### Video Analytics

```python
def track_video_play(self, metadata: VideoMetadata):
    """Track video playback for analytics"""
    event = {
        'type': 'video_play',
        'timestamp': datetime.now(),
        'url': metadata.url,
        'title': metadata.title,
        'video_type': str(metadata.video_type),
    }
    # Send to analytics system
```

## References

- [Qt WebEngine Docs](https://doc.qt.io/qt-6/qtwebengine-index.html)
- [HTML5 Video](https://www.w3schools.com/html/html5_video.asp)
- [Video Formats & Codecs](https://en.wikipedia.org/wiki/Comparison_of_video_container_formats)

## Support

For issues with video playback:
1. Check `VIDEO_PLAYBACK_SUPPORT.md` for diagnostics
2. Review console output for error messages
3. Test with different video sources
4. Check system codec availability

---

**Integration Status:** Ready for implementation  
**Module Version:** 1.0  
**Last Updated:** 2025-12-14
