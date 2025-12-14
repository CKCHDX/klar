"""
Klar Video Support Module
Enhanced video detection, platform identification, and player generation
Supports: YouTube, Vimeo, Dailymotion, Twitch, TikTok, Direct HTML5
"""

import re
from enum import Enum
from typing import Tuple, Optional
from urllib.parse import urlparse, parse_qs


class VideoType(Enum):
    """Supported video platform types"""
    YOUTUBE = "youtube"
    YOUTUBE_SHORT = "youtu_be"
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


class VideoDetector:
    """Detect video content from URLs"""
    
    # Platform detection patterns
    YOUTUBE_PATTERN = r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube-nocookie\.com\/embed\/)([a-zA-Z0-9_-]{11})'
    VIMEO_PATTERN = r'(?:vimeo\.com\/|player\.vimeo\.com\/video\/)([0-9]+)'
    DAILYMOTION_PATTERN = r'(?:dailymotion\.com\/video\/|dai\.ly\/)([a-zA-Z0-9]+)'
    TWITCH_PATTERN = r'(?:twitch\.tv\/|twitch\.tv\/videos\/)([a-zA-Z0-9_-]+)'
    TIKTOK_PATTERN = r'(?:tiktok\.com\/.*?\/)([a-zA-Z0-9]+)(?:\?|$)'
    INSTAGRAM_PATTERN = r'(?:instagram\.com\/p\/|instagram\.com\/reel\/)([a-zA-Z0-9_-]+)'
    
    @staticmethod
    def detect_from_url(url: str) -> Tuple[bool, VideoType, Optional[str]]:
        """
        Detect if URL is a video and identify the type
        Returns: (is_video, video_type, video_id)
        """
        if not url:
            return False, VideoType.UNKNOWN, None
        
        url_lower = url.lower()
        
        # YouTube detection
        if 'youtube' in url_lower or 'youtu.be' in url_lower:
            match = re.search(VideoDetector.YOUTUBE_PATTERN, url)
            if match:
                video_id = match.group(1)
                return True, VideoType.YOUTUBE, video_id
        
        # Vimeo detection
        if 'vimeo' in url_lower:
            match = re.search(VideoDetector.VIMEO_PATTERN, url)
            if match:
                video_id = match.group(1)
                return True, VideoType.VIMEO, video_id
        
        # Dailymotion detection
        if 'dailymotion' in url_lower or 'dai.ly' in url_lower:
            match = re.search(VideoDetector.DAILYMOTION_PATTERN, url)
            if match:
                video_id = match.group(1)
                return True, VideoType.DAILYMOTION, video_id
        
        # Twitch detection
        if 'twitch.tv' in url_lower:
            match = re.search(VideoDetector.TWITCH_PATTERN, url)
            if match:
                video_id = match.group(1)
                return True, VideoType.TWITCH, video_id
        
        # TikTok detection
        if 'tiktok' in url_lower:
            match = re.search(VideoDetector.TIKTOK_PATTERN, url)
            if match:
                video_id = match.group(1)
                return True, VideoType.TIKTOK, video_id
        
        # Instagram detection
        if 'instagram' in url_lower:
            match = re.search(VideoDetector.INSTAGRAM_PATTERN, url)
            if match:
                video_id = match.group(1)
                return True, VideoType.INSTAGRAM, video_id
        
        # Direct file detection
        video_extensions = ['.mp4', '.webm', '.ogv', '.m3u8']
        if any(ext in url_lower for ext in video_extensions):
            if '.m3u8' in url_lower:
                return True, VideoType.HLS_STREAM, None
            elif '.mp4' in url_lower:
                return True, VideoType.HTML5_MP4, None
            elif '.webm' in url_lower:
                return True, VideoType.HTML5_WEBM, None
            elif '.ogv' in url_lower:
                return True, VideoType.HTML5_OGV, None
        
        return False, VideoType.UNKNOWN, None


class VideoMetadata:
    """Extract and manage video metadata"""
    
    def __init__(self, url: str):
        self.url = url
        self.title = self._extract_title()
        self.video_type = self._detect_type()
        self.video_id = self._extract_id()
    
    def _extract_title(self) -> str:
        """Extract video title from URL or filename"""
        # Try to extract title from URL
        parsed = urlparse(self.url)
        
        # From query params (YouTube, etc.)
        if parsed.query:
            params = parse_qs(parsed.query)
            if 'title' in params:
                return params['title'][0]
        
        # From path (filename)
        path = parsed.path.split('/')[-1]
        if path and '.' in path:
            return path.rsplit('.', 1)[0]
        elif path:
            return path.replace('-', ' ').replace('_', ' ')
        
        # Default
        domain = parsed.netloc.replace('www.', '').split('.')[0]
        return f"Video from {domain.capitalize()}"
    
    def _detect_type(self) -> VideoType:
        """Detect video platform type"""
        is_video, vtype, _ = VideoDetector.detect_from_url(self.url)
        return vtype if is_video else VideoType.UNKNOWN
    
    def _extract_id(self) -> Optional[str]:
        """Extract video ID if applicable"""
        _, _, video_id = VideoDetector.detect_from_url(self.url)
        return video_id
    
    def is_embeddable(self) -> bool:
        """Check if video platform supports embedding"""
        embeddable_types = {
            VideoType.YOUTUBE,
            VideoType.VIMEO,
            VideoType.DAILYMOTION,
            VideoType.TWITCH,
            VideoType.TIKTOK,
            VideoType.INSTAGRAM
        }
        return self.video_type in embeddable_types
    
    def is_playable_html5(self) -> bool:
        """Check if video can be played via HTML5"""
        playable_types = {
            VideoType.HTML5_MP4,
            VideoType.HTML5_WEBM,
            VideoType.HTML5_OGV,
            VideoType.HLS_STREAM,
            VideoType.DASH_STREAM
        }
        return self.video_type in playable_types


class VideoPlayer:
    """Generate HTML for video playback"""
    
    @staticmethod
    def generate_embed_html(
        url: str,
        video_type: VideoType,
        video_id: str,
        width: int = 900,
        height: int = 506
    ) -> Optional[str]:
        """
        Generate embed HTML for supported platforms
        """
        if not video_id:
            return None
        
        if video_type == VideoType.YOUTUBE:
            return f'<iframe width="{width}" height="{height}" src="https://www.youtube.com/embed/{video_id}?rel=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
        
        elif video_type == VideoType.VIMEO:
            return f'<iframe src="https://player.vimeo.com/video/{video_id}" width="{width}" height="{height}" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>'
        
        elif video_type == VideoType.DAILYMOTION:
            return f'<iframe src="https://www.dailymotion.com/embed/video/{video_id}" width="{width}" height="{height}" frameborder="0" allow="autoplay" allowfullscreen></iframe>'
        
        elif video_type == VideoType.TWITCH:
            # Twitch embed requires special handling
            return f'<iframe src="https://twitch.tv/{video_id}/chat?parent=localhost" height="500" width="100%" frameborder="0" allowfullscreen></iframe>'
        
        elif video_type == VideoType.TIKTOK:
            return f'<blockquote class="tiktok-embed" cite="https://www.tiktok.com/@{video_id}" data-unique-id="{video_id}" data-embed-type="video"><section></section></blockquote><script async src="https://www.tiktok.com/embed.js"></script>'
        
        elif video_type == VideoType.INSTAGRAM:
            return f'<blockquote class="instagram-media" data-instgrm-permalink="https://www.instagram.com/p/{video_id}/" data-instgrm-version="14"></blockquote><script async src="//www.instagram.com/embed.js"></script>'
        
        return None
    
    @staticmethod
    def generate_html5_player(
        url: str,
        video_type: VideoType,
        title: str = "Video",
        width: str = "100%",
        height: str = "auto"
    ) -> Optional[str]:
        """
        Generate HTML5 video player for direct file playback
        Supports MP4, WebM, OGV, HLS, DASH
        """
        
        # Determine MIME type
        mime_type = "video/mp4"
        if video_type == VideoType.HTML5_WEBM:
            mime_type = "video/webm"
        elif video_type == VideoType.HTML5_OGV:
            mime_type = "video/ogg"
        elif video_type in (VideoType.HLS_STREAM, VideoType.DASH_STREAM):
            mime_type = "application/x-mpegURL"
        
        # Escape URL for HTML
        safe_url = url.replace('"', '&quot;')
        safe_title = title.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_title} - Klar Video Player</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0e1a;
            color: #e8eaf0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .player-container {{
            width: 100%;
            max-width: 1200px;
            background: #131824;
            border-radius: 12px;
            padding: 30px;
            border: 1px solid rgba(59, 130, 246, 0.2);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }}
        .player-title {{
            color: #3b82f6;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
            word-break: break-word;
        }}
        .video-wrapper {{
            position: relative;
            width: 100%;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            border-radius: 8px;
            background: #000;
        }}
        .video-wrapper video {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 8px;
        }}
        .controls-info {{
            color: #a0a8c0;
            font-size: 12px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(59, 130, 246, 0.2);
        }}
        .control-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        .control-item {{
            font-size: 11px;
            padding: 5px 0;
        }}
        .control-item strong {{
            color: #3b82f6;
        }}
    </style>
</head>
<body>
    <div class="player-container">
        <div class="player-title">\u25b6 {safe_title}</div>
        <div class="video-wrapper">
            <video controls controlsList="nodownload" crossorigin="anonymous" preload="metadata" style="background: #000;">
                <source src="{safe_url}" type="{mime_type}">
                Your browser does not support HTML5 video playback.
            </video>
        </div>
        <div class="controls-info">
            <strong>Keyboard Controls:</strong>
            <div class="control-list">
                <div class="control-item"><strong>Space</strong> - Play/Pause</div>
                <div class="control-item"><strong>\u2192</strong> - Forward 5s</div>
                <div class="control-item"><strong>\u2190</strong> - Rewind 5s</div>
                <div class="control-item"><strong>f</strong> - Fullscreen</div>
                <div class="control-item"><strong>m</strong> - Mute</div>
                <div class="control-item"><strong>\u2191/\u2193</strong> - Volume</div>
                <div class="control-item"><strong>&gt;</strong> - Speed Up</div>
                <div class="control-item"><strong>&lt;</strong> - Speed Down</div>
            </div>
        </div>
    </div>
    <script>
        const video = document.querySelector('video');
        
        document.addEventListener('keydown', (e) => {{
            if (e.target !== document.body) return;
            
            switch(e.key) {{
                case ' ':
                    e.preventDefault();
                    video.paused ? video.play() : video.pause();
                    break;
                case 'ArrowRight':
                    video.currentTime += 5;
                    break;
                case 'ArrowLeft':
                    video.currentTime -= 5;
                    break;
                case 'f':
                    e.preventDefault();
                    if (video.requestFullscreen) {{
                        video.requestFullscreen();
                    }}
                    break;
                case 'm':
                    video.muted = !video.muted;
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    video.volume = Math.min(1, video.volume + 0.1);
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    video.volume = Math.max(0, video.volume - 0.1);
                    break;
                case '>':
                case '.':
                    video.playbackRate = Math.min(2, video.playbackRate + 0.25);
                    break;
                case '<':
                case ',':
                    video.playbackRate = Math.max(0.25, video.playbackRate - 0.25);
                    break;
            }}
        }});
        
        document.addEventListener('fullscreenchange', () => {{
            if (!document.fullscreenElement) {{
            }}
        }});
    </script>
</body>
</html>
'''
        return html
    
    @staticmethod
    def generate_simple_player(url: str, title: str = "Video") -> str:
        """
        Generate a minimal video player for fallback use
        """
        safe_url = url.replace('"', '&quot;')
        safe_title = title.replace('"', '&quot;')
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0; padding: 20px;
            background: #0a0e1a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        video {{
            max-width: 90vw;
            max-height: 90vh;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }}
    </style>
</head>
<body>
    <video controls crossorigin="anonymous" preload="metadata" style="width: 100%; max-width: 1200px;">
        <source src="{safe_url}">
        Your browser does not support HTML5 video.
    </video>
</body>
</html>
'''
