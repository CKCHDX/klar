"""
Video Support Module for Klar Browser
Handles video detection, platform identification, and playback optimization
Version 1.0
"""

import re
from typing import Dict, Optional, Tuple, List
from enum import Enum


class VideoType(Enum):
    """Video type enumeration"""
    MP4 = "video/mp4"
    WEBM = "video/webm"
    OGV = "video/ogg"
    QUICKTIME = "video/quicktime"
    MATROSKA = "video/x-matroska"
    AVI = "video/x-msvideo"
    FLV = "video/x-flv"
    HLS = "application/x-mpegURL"
    DASH = "application/dash+xml"
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    TWITCH = "twitch"
    TIKTOK = "tiktok"
    UNKNOWN = "unknown"


class VideoDetector:
    """Detect and identify video content from URLs"""
    
    # Video file extensions mapped to MIME types
    VIDEO_EXTENSIONS = {
        '.mp4': VideoType.MP4,
        '.m4v': VideoType.MP4,
        '.webm': VideoType.WEBM,
        '.ogv': VideoType.OGV,
        '.ogg': VideoType.OGV,
        '.mov': VideoType.QUICKTIME,
        '.mkv': VideoType.MATROSKA,
        '.avi': VideoType.AVI,
        '.flv': VideoType.FLV,
        '.m3u8': VideoType.HLS,
        '.mpd': VideoType.DASH,
        '.ts': VideoType.HLS,
        '.m2ts': VideoType.HLS,
    }
    
    # Streaming platform patterns
    PLATFORMS = {
        'youtube': {
            'patterns': [
                r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?(?:.*&)?v=([\w-_]{11})',
                r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([\w-_]{11})',
                r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([\w-_]{11})',
            ],
            'video_type': VideoType.YOUTUBE,
            'supports_embed': True,
            'embed_template': 'https://www.youtube-nocookie.com/embed/{video_id}?autoplay=1&rel=0&modestbranding=1',
        },
        'vimeo': {
            'patterns': [
                r'(?:https?:\/\/)?(?:www\.)?vimeo\.com\/(\d+)',
                r'(?:https?:\/\/)?player\.vimeo\.com\/video\/(\d+)',
            ],
            'video_type': VideoType.VIMEO,
            'supports_embed': True,
            'embed_template': 'https://player.vimeo.com/video/{video_id}?autoplay=1&byline=0&portrait=0',
        },
        'dailymotion': {
            'patterns': [
                r'(?:https?:\/\/)?(?:www\.)?dailymotion\.com\/video\/([a-z0-9]+)',
            ],
            'video_type': VideoType.DAILYMOTION,
            'supports_embed': True,
            'embed_template': 'https://www.dailymotion.com/embed/video/{video_id}?autoplay=1',
        },
        'twitch': {
            'patterns': [
                r'(?:https?:\/\/)?(?:www\.)?twitch\.tv\/([a-zA-Z0-9_]+)(?:\/|$)',
                r'(?:https?:\/\/)?(?:www\.)?twitch\.tv\/videos\/([0-9]+)',
            ],
            'video_type': VideoType.TWITCH,
            'supports_embed': True,
            'embed_template': 'https://player.twitch.tv/?channel={video_id}&parent=localhost',
        },
        'tiktok': {
            'patterns': [
                r'(?:https?:\/\/)?(?:www\.)?tiktok\.com\/@[^/]+\/video\/(\d+)',
            ],
            'video_type': VideoType.TIKTOK,
            'supports_embed': True,
            'embed_template': 'https://www.tiktok.com/embed/v2/{video_id}',
        },
    }
    
    @staticmethod
    def detect_from_url(url: str) -> Tuple[bool, Optional[VideoType], Optional[str]]:
        """
        Detect if URL is a video and return type and ID
        Returns: (is_video, video_type, video_id)
        """
        if not url:
            return False, None, None
        
        url_lower = url.lower()
        
        # Check file extensions first
        for ext, vtype in VideoDetector.VIDEO_EXTENSIONS.items():
            if ext in url_lower:
                return True, vtype, None
        
        # Check streaming platforms
        for platform_name, platform_config in VideoDetector.PLATFORMS.items():
            for pattern in platform_config['patterns']:
                match = re.search(pattern, url)
                if match:
                    video_id = match.group(1)
                    return True, platform_config['video_type'], video_id
        
        return False, None, None
    
    @staticmethod
    def get_mime_type(video_type: VideoType) -> str:
        """Get MIME type for video type"""
        return video_type.value if hasattr(video_type, 'value') else str(video_type)
    
    @staticmethod
    def is_streamable_format(video_type: VideoType) -> bool:
        """Check if format supports streaming"""
        streamable = [VideoType.HLS, VideoType.DASH, VideoType.MP4, VideoType.WEBM]
        return video_type in streamable
    
    @staticmethod
    def is_embedding_platform(video_type: VideoType) -> bool:
        """Check if video is from an embedding platform"""
        embedding = [
            VideoType.YOUTUBE, VideoType.VIMEO, VideoType.DAILYMOTION,
            VideoType.TWITCH, VideoType.TIKTOK
        ]
        return video_type in embedding


class VideoPlayer:
    """Generate player HTML and handles playback"""
    
    @staticmethod
    def generate_html5_player(url: str, video_type: VideoType, title: str = "Video") -> str:
        """
        Generate HTML5 video player for direct playback
        """
        if not video_type or not video_type.value.startswith('video/'):
            return ""
        
        mime_type = VideoDetector.get_mime_type(video_type)
        
        return f'''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Klar Video Player</title>
    <style>
        * {{
            margin: 0; padding: 0; box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e1a;
            color: #e8eaf0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            width: 100%;
            max-width: 1200px;
        }}
        .player {{
            background: #000;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 20px;
            box-shadow: 0 20px 60px rgba(59, 130, 246, 0.2);
        }}
        video {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .info {{
            background: #1e2538;
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 12px;
            padding: 20px;
        }}
        .title {{
            font-size: 24px;
            font-weight: 600;
            color: #3b82f6;
            margin-bottom: 10px;
        }}
        .details {{
            font-size: 13px;
            color: #6b7390;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="player">
            <video controls autoplay crossorigin="anonymous">
                <source src="{url}" type="{mime_type}">
                Your browser doesn't support HTML5 video playback.
            </video>
        </div>
        <div class="info">
            <div class="title">{title}</div>
            <div class="details">✓ Playing: {mime_type}</div>
        </div>
    </div>
    <script>
        const video = document.querySelector('video');
        document.addEventListener('keydown', (e) => {{
            switch(e.key) {{
                case ' ': e.preventDefault(); video.paused ? video.play() : video.pause(); break;
                case 'f': video.requestFullscreen(); break;
                case 'm': video.muted = !video.muted; break;
                case 'ArrowRight': video.currentTime += 5; break;
                case 'ArrowLeft': video.currentTime -= 5; break;
            }}
        }});
    </script>
</body>
</html>'''
    
    @staticmethod
    def generate_embed_html(url: str, video_type: VideoType, video_id: Optional[str], width: int = 800, height: int = 450) -> Optional[str]:
        """
        Generate embedded player for streaming platforms
        """
        if not video_id:
            return None
        
        # YouTube
        if video_type == VideoType.YOUTUBE:
            return f'''<iframe width="{width}" height="{height}" src="https://www.youtube-nocookie.com/embed/{video_id}?autoplay=1&rel=0&modestbranding=1" frameborder="0" allowfullscreen allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" loading="lazy"></iframe>'''
        
        # Vimeo
        elif video_type == VideoType.VIMEO:
            return f'''<iframe width="{width}" height="{height}" src="https://player.vimeo.com/video/{video_id}?autoplay=1&byline=0&portrait=0" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen loading="lazy"></iframe>'''
        
        # Dailymotion
        elif video_type == VideoType.DAILYMOTION:
            return f'''<iframe width="{width}" height="{height}" src="https://www.dailymotion.com/embed/video/{video_id}?autoplay=1" frameborder="0" allowfullscreen allow="autoplay" loading="lazy"></iframe>'''
        
        # Twitch
        elif video_type == VideoType.TWITCH:
            return f'''<iframe width="{width}" height="{height}" src="https://player.twitch.tv/?channel={video_id}&parent=localhost" frameborder="0" allowfullscreen allow="autoplay" loading="lazy"></iframe>'''
        
        return None


class VideoMetadata:
    """Extract and store video metadata"""
    
    def __init__(self, url: str):
        self.url = url
        self.is_video, self.video_type, self.video_id = VideoDetector.detect_from_url(url)
        self.title = self._extract_title()
        self.mime_type = VideoDetector.get_mime_type(self.video_type) if self.video_type else None
    
    def _extract_title(self) -> str:
        """Extract title from URL or generate default"""
        if self.video_type == VideoType.YOUTUBE:
            return "YouTube Video"
        elif self.video_type == VideoType.VIMEO:
            return "Vimeo Video"
        elif self.video_type == VideoType.TWITCH:
            return "Twitch Stream"
        elif self.video_type == VideoType.TIKTOK:
            return "TikTok Video"
        elif self.video_type:
            return f"Video - {self.video_type.name}"
        return "Video"
    
    def is_embeddable(self) -> bool:
        """Check if video can be embedded"""
        return (
            self.is_video and
            self.video_type and
            VideoDetector.is_embedding_platform(self.video_type)
        )
    
    def is_playable_html5(self) -> bool:
        """Check if video can be played directly"""
        return (
            self.is_video and
            self.video_type and
            self.video_type.value.startswith('video/')
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'url': self.url,
            'is_video': self.is_video,
            'type': self.video_type.name if self.video_type else None,
            'video_id': self.video_id,
            'title': self.title,
            'mime_type': self.mime_type,
            'is_embeddable': self.is_embeddable(),
            'is_playable_html5': self.is_playable_html5(),
        }
