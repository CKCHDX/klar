"""
Klar Video Support Module - WHITELISTED DOMAINS ONLY
Video detection and playback for whitelisted Swedish domains only
Supports: SVT, SR, UR, Filmstaden, Blockflix, and direct video files on whitelisted domains

VIDEO POLICY: Only plays videos from whitelisted domains in domains.json
No YouTube, no external services - strictly Swedish whitelisted sources
"""

import re
from enum import Enum
from typing import Tuple, Optional
from urllib.parse import urlparse, parse_qs


class VideoType(Enum):
    """Supported video types for whitelisted domains"""
    # Swedish public broadcasters
    SVT = "svt"  # SVT Play - Swedish Television
    SR = "sr"    # Sveriges Radio - Radio streams
    UR = "ur"    # Educational Broadcasting
    
    # Swedish streaming services
    FILMSTADEN = "filmstaden"  # Cinema
    BLOCKFLIX = "blockflix"    # Swedish streaming
    
    # Direct files on whitelisted domains
    HTML5_MP4 = "mp4"
    HTML5_WEBM = "webm"
    HTML5_OGV = "ogv"
    HLS_STREAM = "hls"
    DASH_STREAM = "dash"
    
    # Status
    BLOCKED = "blocked"  # Domain not whitelisted
    UNKNOWN = "unknown"


class VideoDetector:
    """Detect video content from URLs - WHITELISTED DOMAINS ONLY"""
    
    # Whitelisted domain patterns (from domains.json)
    WHITELISTED_DOMAINS = {
        'svt.se': 'SVT (Swedish Television)',
        'sverigesradio.se': 'SR (Sveriges Radio)',
        'ur.se': 'UR (Educational)',
        'filmstaden.se': 'Filmstaden (Cinema)',
        'sverigestelevision.se': 'SVT',
    }
    
    @staticmethod
    def is_whitelisted_domain(url: str) -> Tuple[bool, str]:
        """
        Check if URL is from a whitelisted domain
        Returns: (is_whitelisted, domain_name)
        """
        try:
            parsed = urlparse(url.lower())
            netloc = parsed.netloc.replace('www.', '')
            
            # Check against whitelisted domains
            for domain, name in VideoDetector.WHITELISTED_DOMAINS.items():
                if domain in netloc or netloc.endswith(domain):
                    return True, domain
            
            # Check if any part matches
            for domain in VideoDetector.WHITELISTED_DOMAINS.keys():
                if domain in netloc:
                    return True, domain
            
            return False, netloc
        except:
            return False, ""
    
    @staticmethod
    def detect_from_url(url: str) -> Tuple[bool, VideoType, Optional[str]]:
        """
        Detect if URL is a video and identify the type
        CRITICAL: Only processes whitelisted domains
        
        Returns: (is_video, video_type, video_id)
        """
        if not url:
            return False, VideoType.UNKNOWN, None
        
        url_lower = url.lower()
        
        # SECURITY CHECK: Is this domain whitelisted?
        is_whitelisted, domain = VideoDetector.is_whitelisted_domain(url)
        if not is_whitelisted:
            return False, VideoType.BLOCKED, None
        
        # Domain is whitelisted - now check for video content
        
        # SVT (Swedish Television) detection
        if 'svt.se' in url_lower:
            if 'play.svt.se' in url_lower or '/video/' in url_lower:
                # Extract video ID if present
                video_id = VideoDetector._extract_id_from_path(url)
                return True, VideoType.SVT, video_id
        
        # SR (Sveriges Radio) detection
        if 'sverigesradio.se' in url_lower or 'sr.se' in url_lower:
            if '/sida/' in url_lower or '/artikel/' in url_lower:
                video_id = VideoDetector._extract_id_from_path(url)
                return True, VideoType.SR, video_id
        
        # UR (Educational) detection
        if 'ur.se' in url_lower:
            if '/play/' in url_lower or '/video/' in url_lower:
                video_id = VideoDetector._extract_id_from_path(url)
                return True, VideoType.UR, video_id
        
        # Filmstaden detection
        if 'filmstaden.se' in url_lower:
            if '/watch/' in url_lower or '/film/' in url_lower:
                video_id = VideoDetector._extract_id_from_path(url)
                return True, VideoType.FILMSTADEN, video_id
        
        # Direct file detection (on whitelisted domains)
        if '.mp4' in url_lower:
            return True, VideoType.HTML5_MP4, None
        elif '.webm' in url_lower:
            return True, VideoType.HTML5_WEBM, None
        elif '.ogv' in url_lower:
            return True, VideoType.HTML5_OGV, None
        elif '.m3u8' in url_lower:
            return True, VideoType.HLS_STREAM, None
        elif '.mpd' in url_lower:
            return True, VideoType.DASH_STREAM, None
        
        return False, VideoType.UNKNOWN, None
    
    @staticmethod
    def _extract_id_from_path(url: str) -> Optional[str]:
        """Extract video ID from URL path"""
        try:
            # Try to extract last path segment as ID
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]
            if path_parts:
                return path_parts[-1]
            return None
        except:
            return None


class VideoMetadata:
    """Extract and manage video metadata - WHITELISTED ONLY"""
    
    def __init__(self, url: str):
        self.url = url
        self.is_whitelisted, self.domain = VideoDetector.is_whitelisted_domain(url)
        self.title = self._extract_title()
        self.video_type = self._detect_type()
        self.video_id = self._extract_id()
    
    def _extract_title(self) -> str:
        """Extract video title from URL or filename"""
        parsed = urlparse(self.url)
        
        # From query params
        if parsed.query:
            params = parse_qs(parsed.query)
            if 'title' in params:
                return params['title'][0]
        
        # From path (filename)
        path = parsed.path.split('/')[-1]
        if path and '.' in path:
            return path.rsplit('.', 1)[0].replace('-', ' ').replace('_', ' ')
        elif path:
            return path.replace('-', ' ').replace('_', ' ')
        
        # Default: domain name
        return f"Video från {self.domain}"
    
    def _detect_type(self) -> VideoType:
        """Detect video platform type"""
        is_video, vtype, _ = VideoDetector.detect_from_url(self.url)
        return vtype if is_video else VideoType.UNKNOWN
    
    def _extract_id(self) -> Optional[str]:
        """Extract video ID if applicable"""
        _, _, video_id = VideoDetector.detect_from_url(self.url)
        return video_id
    
    def can_play(self) -> bool:
        """Check if video can be played (whitelisted AND valid type)"""
        if not self.is_whitelisted:
            return False
        
        playable_types = {
            VideoType.SVT,
            VideoType.SR,
            VideoType.UR,
            VideoType.FILMSTADEN,
            VideoType.HTML5_MP4,
            VideoType.HTML5_WEBM,
            VideoType.HTML5_OGV,
            VideoType.HLS_STREAM,
            VideoType.DASH_STREAM
        }
        return self.video_type in playable_types


class VideoPlayer:
    """Generate HTML for video playback - WHITELISTED DOMAINS ONLY"""
    
    @staticmethod
    def generate_player_html(
        url: str,
        video_type: VideoType,
        title: str = "Video",
        width: str = "100%",
        height: str = "auto"
    ) -> Optional[str]:
        """
        Generate HTML5 video player for whitelisted domain video files
        """
        if video_type == VideoType.BLOCKED:
            return VideoPlayer._generate_blocked_html(url)
        
        if video_type in (VideoType.UNKNOWN, VideoType.BLOCKED):
            return None
        
        # For direct files (MP4, WebM, etc.)
        if video_type in (VideoType.HTML5_MP4, VideoType.HTML5_WEBM, VideoType.HTML5_OGV, 
                          VideoType.HLS_STREAM, VideoType.DASH_STREAM):
            return VideoPlayer._generate_html5_player(url, video_type, title)
        
        # For Swedish streaming services
        if video_type == VideoType.SVT:
            return VideoPlayer._generate_svt_player(url, title)
        elif video_type == VideoType.SR:
            return VideoPlayer._generate_sr_player(url, title)
        elif video_type == VideoType.UR:
            return VideoPlayer._generate_ur_player(url, title)
        elif video_type == VideoType.FILMSTADEN:
            return VideoPlayer._generate_filmstaden_player(url, title)
        
        return None
    
    @staticmethod
    def _generate_blocked_html(url: str) -> str:
        """Generate blocked domain warning"""
        safe_url = url.replace('"', '&quot;')
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
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
        .container {{
            max-width: 600px;
            background: #131824;
            border: 2px solid #ef4444;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
        }}
        .icon {{ font-size: 60px; margin-bottom: 20px; }}
        h1 {{ color: #ef4444; margin-bottom: 10px; }}
        p {{ color: #a0a8c0; line-height: 1.6; }}
        .reason {{ background: rgba(239, 68, 68, 0.1); padding: 15px; border-radius: 8px; margin: 20px 0; color: #fca5a5; }}
        .note {{ background: rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 8px; margin: 20px 0; color: #93c5fd; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🔒</div>
        <h1>Video från denna domän är blockerad</h1>
        <p>Klar tillåter endast video från godkända svenska domäner för din säkerhet.</p>
        <div class="reason">
            <strong>URL:</strong> {safe_url}
        </div>
        <div class="note">
            <strong>Tillåtna videokällor:</strong>
            <br>SVT.se, SR.se, UR.se, Filmstaden.se och andra godkända svenska webbplatser
        </div>
    </div>
</body>
</html>
'''
    
    @staticmethod
    def _generate_html5_player(url: str, video_type: VideoType, title: str) -> str:
        """Generate HTML5 video player for direct file playback"""
        mime_type = "video/mp4"
        if video_type == VideoType.HTML5_WEBM:
            mime_type = "video/webm"
        elif video_type == VideoType.HTML5_OGV:
            mime_type = "video/ogg"
        elif video_type in (VideoType.HLS_STREAM, VideoType.DASH_STREAM):
            mime_type = "application/x-mpegURL"
        
        safe_url = url.replace('"', '&quot;')
        safe_title = title.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_title} - Klar Video</title>
    <style>
        * {{
            margin: 0; padding: 0; box-sizing: border-box;
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
        .container {{
            width: 100%;
            max-width: 1200px;
            background: #131824;
            border-radius: 12px;
            padding: 30px;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }}
        .title {{
            color: #3b82f6;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
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
            top: 0; left: 0;
            width: 100%;
            height: 100%;
        }}
        .controls {{
            color: #a0a8c0;
            font-size: 12px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(59, 130, 246, 0.2);
        }}
        .klar-badge {{
            display: inline-block;
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid #3b82f6;
            color: #60a5fa;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="klar-badge">✓ Godkänd svensk källa</div>
        <div class="title">{safe_title}</div>
        <div class="video-wrapper">
            <video controls preload="metadata" style="background: #000;">
                <source src="{safe_url}" type="{mime_type}">
                Din webbläsare stöder inte HTML5 videospelning.
            </video>
        </div>
        <div class="controls">
            <strong>Tangentbordskontroller:</strong><br>
            Space = Spela/Pausa | ← / → = Spola | f = Fullskärm | m = Ljud av
        </div>
    </div>
</body>
</html>
'''
    
    @staticmethod
    def _generate_svt_player(url: str, title: str) -> str:
        """Generate SVT Play player - direct link to SVT"""
        safe_url = url.replace('"', '&quot;')
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
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
        .container {{
            text-align: center;
            background: #131824;
            padding: 40px;
            border-radius: 12px;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }}
        .logo {{ font-size: 60px; margin-bottom: 20px; }}
        h1 {{ color: #3b82f6; margin-bottom: 20px; }}
        p {{ color: #a0a8c0; margin-bottom: 20px; }}
        .btn {{
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.2s;
        }}
        .btn:hover {{ background: #60a5fa; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📺</div>
        <h1>SVT Play</h1>
        <p>Denna video kräver SVT Play för uppspelning.</p>
        <a href="{safe_url}" class="btn" target="_blank">Öppna i SVT Play →</a>
    </div>
</body>
</html>
'''
    
    @staticmethod
    def _generate_sr_player(url: str, title: str) -> str:
        """Generate SR player - direct link to Sveriges Radio"""
        safe_url = url.replace('"', '&quot;')
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
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
        .container {{
            text-align: center;
            background: #131824;
            padding: 40px;
            border-radius: 12px;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }}
        .logo {{ font-size: 60px; margin-bottom: 20px; }}
        h1 {{ color: #3b82f6; margin-bottom: 20px; }}
        p {{ color: #a0a8c0; margin-bottom: 20px; }}
        .btn {{
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📻</div>
        <h1>Sveriges Radio</h1>
        <p>Klicka nedan för att lyssna på Sveriges Radio.</p>
        <a href="{safe_url}" class="btn" target="_blank">Öppna i SR →</a>
    </div>
</body>
</html>
'''
    
    @staticmethod
    def _generate_ur_player(url: str, title: str) -> str:
        """Generate UR player - direct link to UR"""
        safe_url = url.replace('"', '&quot;')
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
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
        .container {{
            text-align: center;
            background: #131824;
            padding: 40px;
            border-radius: 12px;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }}
        .logo {{ font-size: 60px; margin-bottom: 20px; }}
        h1 {{ color: #3b82f6; margin-bottom: 20px; }}
        p {{ color: #a0a8c0; margin-bottom: 20px; }}
        .btn {{
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎓</div>
        <h1>UR - Utbildningsradion</h1>
        <p>Klicka nedan för att se innehållet på UR.</p>
        <a href="{safe_url}" class="btn" target="_blank">Öppna i UR →</a>
    </div>
</body>
</html>
'''
    
    @staticmethod
    def _generate_filmstaden_player(url: str, title: str) -> str:
        """Generate Filmstaden player - direct link"""
        safe_url = url.replace('"', '&quot;')
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
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
        .container {{
            text-align: center;
            background: #131824;
            padding: 40px;
            border-radius: 12px;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }}
        .logo {{ font-size: 60px; margin-bottom: 20px; }}
        h1 {{ color: #3b82f6; margin-bottom: 20px; }}
        p {{ color: #a0a8c0; margin-bottom: 20px; }}
        .btn {{
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎬</div>
        <h1>Filmstaden</h1>
        <p>Se filmen på Filmstaden.</p>
        <a href="{safe_url}" class="btn" target="_blank">Öppna i Filmstaden →</a>
    </div>
</body>
</html>
'''
