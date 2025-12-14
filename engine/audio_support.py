"""
Klar Audio Support Module - WHITELISTED DOMAINS ONLY
Audio detection and playback for whitelisted Swedish domains only
Supports: SR (Swedish Radio), Spotify, Tidal, direct audio files on whitelisted domains

AUDIO POLICY: Only plays audio from whitelisted domains in domains.json
No external services - strictly Swedish whitelisted sources
"""

import re
from enum import Enum
from typing import Tuple, Optional
from urllib.parse import urlparse, parse_qs


class AudioType(Enum):
    """Supported audio types for whitelisted domains"""
    # Swedish public broadcasters & streaming
    SR = "sr"                    # Sveriges Radio
    SPOTIFY = "spotify"          # Spotify (whitelisted)
    TIDAL = "tidal"              # Tidal (whitelisted)
    
    # Direct audio files on whitelisted domains
    HTML5_MP3 = "mp3"
    HTML5_WAV = "wav"
    HTML5_OGG = "ogg"
    HTML5_FLAC = "flac"
    HTML5_M4A = "m4a"
    
    # Streaming formats
    HLS_AUDIO = "hls_audio"      # HLS audio streams (.m3u8)
    
    # Status
    BLOCKED = "blocked"          # Domain not whitelisted
    UNKNOWN = "unknown"


class AudioDetector:
    """Detect audio content from URLs - WHITELISTED DOMAINS ONLY"""
    
    # Whitelisted domain patterns (from domains.json)
    WHITELISTED_DOMAINS = {
        'sverigesradio.se': 'SR (Sveriges Radio)',
        'spotify.com': 'Spotify',
        'tidal.com': 'Tidal',
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
            for domain, name in AudioDetector.WHITELISTED_DOMAINS.items():
                if domain in netloc or netloc.endswith(domain):
                    return True, domain
            
            return False, netloc
        except:
            return False, ""
    
    @staticmethod
    def detect_from_url(url: str) -> Tuple[bool, AudioType, Optional[str]]:
        """
        Detect if URL is audio and identify the type
        CRITICAL: Only processes whitelisted domains
        
        Returns: (is_audio, audio_type, audio_id)
        """
        if not url:
            return False, AudioType.UNKNOWN, None
        
        url_lower = url.lower()
        
        # SECURITY CHECK: Is this domain whitelisted?
        is_whitelisted, domain = AudioDetector.is_whitelisted_domain(url)
        if not is_whitelisted:
            return False, AudioType.BLOCKED, None
        
        # Domain is whitelisted - now check for audio content
        
        # SR (Sveriges Radio) detection
        if 'sverigesradio.se' in url_lower or 'sr.se' in url_lower:
            if '/sida/' in url_lower or '/artikel/' in url_lower or '/podcast/' in url_lower:
                audio_id = AudioDetector._extract_id_from_path(url)
                return True, AudioType.SR, audio_id
        
        # Spotify detection
        if 'spotify.com' in url_lower:
            if '/track/' in url_lower or '/album/' in url_lower or '/playlist/' in url_lower:
                audio_id = AudioDetector._extract_id_from_path(url)
                return True, AudioType.SPOTIFY, audio_id
        
        # Tidal detection
        if 'tidal.com' in url_lower:
            if '/track/' in url_lower or '/album/' in url_lower or '/playlist/' in url_lower:
                audio_id = AudioDetector._extract_id_from_path(url)
                return True, AudioType.TIDAL, audio_id
        
        # Direct audio file detection (on whitelisted domains)
        if '.mp3' in url_lower:
            return True, AudioType.HTML5_MP3, None
        elif '.wav' in url_lower:
            return True, AudioType.HTML5_WAV, None
        elif '.ogg' in url_lower or '.oga' in url_lower:
            return True, AudioType.HTML5_OGG, None
        elif '.flac' in url_lower:
            return True, AudioType.HTML5_FLAC, None
        elif '.m4a' in url_lower or '.aac' in url_lower:
            return True, AudioType.HTML5_M4A, None
        elif '.m3u8' in url_lower and ('audio' in url_lower or 'stream' in url_lower or 'radio' in url_lower):
            return True, AudioType.HLS_AUDIO, None
        
        return False, AudioType.UNKNOWN, None
    
    @staticmethod
    def _extract_id_from_path(url: str) -> Optional[str]:
        """Extract audio ID from URL path"""
        try:
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]
            if path_parts:
                return path_parts[-1]
            return None
        except:
            return None


class AudioMetadata:
    """Extract and manage audio metadata - WHITELISTED ONLY"""
    
    def __init__(self, url: str):
        self.url = url
        self.is_whitelisted, self.domain = AudioDetector.is_whitelisted_domain(url)
        self.title = self._extract_title()
        self.audio_type = self._detect_type()
        self.audio_id = self._extract_id()
    
    def _extract_title(self) -> str:
        """Extract audio title from URL or filename"""
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
        return f"Ljud från {self.domain}"
    
    def _detect_type(self) -> AudioType:
        """Detect audio type"""
        is_audio, atype, _ = AudioDetector.detect_from_url(self.url)
        return atype if is_audio else AudioType.UNKNOWN
    
    def _extract_id(self) -> Optional[str]:
        """Extract audio ID if applicable"""
        _, _, audio_id = AudioDetector.detect_from_url(self.url)
        return audio_id
    
    def can_play(self) -> bool:
        """Check if audio can be played (whitelisted AND valid type)"""
        if not self.is_whitelisted:
            return False
        
        playable_types = {
            AudioType.SR,
            AudioType.SPOTIFY,
            AudioType.TIDAL,
            AudioType.HTML5_MP3,
            AudioType.HTML5_WAV,
            AudioType.HTML5_OGG,
            AudioType.HTML5_FLAC,
            AudioType.HTML5_M4A,
            AudioType.HLS_AUDIO,
        }
        return self.audio_type in playable_types


class AudioPlayer:
    """Generate HTML for audio playback - WHITELISTED DOMAINS ONLY"""
    
    @staticmethod
    def generate_player_html(
        url: str,
        audio_type: AudioType,
        title: str = "Audio",
    ) -> Optional[str]:
        """
        Generate HTML audio player for whitelisted domain audio files
        """
        if audio_type == AudioType.BLOCKED:
            return AudioPlayer._generate_blocked_html(url)
        
        if audio_type in (AudioType.UNKNOWN, AudioType.BLOCKED):
            return None
        
        # For direct audio files (MP3, WAV, OGG, etc.)
        if audio_type in (AudioType.HTML5_MP3, AudioType.HTML5_WAV, AudioType.HTML5_OGG,
                          AudioType.HTML5_FLAC, AudioType.HTML5_M4A, AudioType.HLS_AUDIO):
            return AudioPlayer._generate_html5_player(url, audio_type, title)
        
        # For Swedish streaming services
        if audio_type == AudioType.SR:
            return AudioPlayer._generate_sr_player(url, title)
        elif audio_type == AudioType.SPOTIFY:
            return AudioPlayer._generate_spotify_player(url, title)
        elif audio_type == AudioType.TIDAL:
            return AudioPlayer._generate_tidal_player(url, title)
        
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
        <h1>Ljud från denna domän är blockerad</h1>
        <p>Klar tillåter endast ljud från godkända svenska domäner för din säkerhet.</p>
        <div class="reason">
            <strong>URL:</strong> {safe_url}
        </div>
        <div class="note">
            <strong>Tillåtna ljudkällor:</strong>
            <br>SR.se, Spotify.com, Tidal.com och andra godkända svenska webbplatser
        </div>
    </div>
</body>
</html>
'''
    
    @staticmethod
    def _generate_html5_player(url: str, audio_type: AudioType, title: str) -> str:
        """Generate HTML5 audio player for direct file playback"""
        mime_type = "audio/mpeg"
        if audio_type == AudioType.HTML5_WAV:
            mime_type = "audio/wav"
        elif audio_type == AudioType.HTML5_OGG:
            mime_type = "audio/ogg"
        elif audio_type == AudioType.HTML5_FLAC:
            mime_type = "audio/flac"
        elif audio_type == AudioType.HTML5_M4A:
            mime_type = "audio/mp4"
        elif audio_type == AudioType.HLS_AUDIO:
            mime_type = "application/x-mpegURL"
        
        safe_url = url.replace('"', '&quot;')
        safe_title = title.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_title} - Klar Audio</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0a0e1a 0%, #1a2032 100%);
            color: #e8eaf0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            width: 100%;
            max-width: 600px;
            background: #131824;
            border-radius: 16px;
            padding: 40px;
            border: 1px solid rgba(59, 130, 246, 0.2);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }}
        .badge {{
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
        .title {{
            color: #3b82f6;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 25px;
            word-break: break-word;
        }}
        .player-wrapper {{
            background: #1e2538;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        audio {{
            width: 100%;
            border-radius: 8px;
        }}
        .controls {{
            color: #a0a8c0;
            font-size: 12px;
            padding-top: 15px;
            border-top: 1px solid rgba(59, 130, 246, 0.2);
        }}
        .controls strong {{ color: #3b82f6; }}
        .keyboard-info {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 10px;
        }}
        .key {{
            font-size: 11px;
            padding: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="badge">✓ Godkänd svensk källa</div>
        <div class="title">🔊 {safe_title}</div>
        <div class="player-wrapper">
            <audio controls preload="metadata" crossorigin="anonymous">
                <source src="{safe_url}" type="{mime_type}">
                Din webbläsare stöder inte HTML5 audiouppspelning.
            </audio>
        </div>
        <div class="controls">
            <strong>Tangentbordskontroller:</strong>
            <div class="keyboard-info">
                <div class="key"><strong>Space</strong> - Spela/Pausa</div>
                <div class="key"><strong>→/←</strong> - Spola</div>
                <div class="key"><strong>m</strong> - Ljud av</div>
                <div class="key"><strong>↑/↓</strong> - Volym</div>
                <div class="key"><strong>></strong> - Snabbare</div>
                <div class="key"><strong><</strong> - Långsammare</div>
            </div>
        </div>
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0a0e1a 0%, #1a2032 100%);
            color: #e8eaf0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 500px;
            background: #131824;
            border-radius: 16px;
            padding: 50px;
            text-align: center;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }}
        .logo {{ font-size: 80px; margin-bottom: 20px; }}
        h1 {{ color: #3b82f6; margin-bottom: 20px; font-size: 28px; }}
        p {{ color: #a0a8c0; margin-bottom: 20px; line-height: 1.6; }}
        .btn {{
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 14px 28px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.2s;
        }}
        .btn:hover {{ background: #60a5fa; }}
        .info {{ color: #6b7390; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📻</div>
        <h1>Sveriges Radio</h1>
        <p>Lyssna på Sveriges Radio</p>
        <a href="{safe_url}" class="btn" target="_blank">Öppna i SR →</a>
        <div class="info">Klicka för att öppna i Sverige Radio</div>
    </div>
</body>
</html>
'''
    
    @staticmethod
    def _generate_spotify_player(url: str, title: str) -> str:
        """Generate Spotify player - direct link"""
        safe_url = url.replace('"', '&quot;')
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0a0e1a 0%, #1a2032 100%);
            color: #e8eaf0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 500px;
            background: #131824;
            border-radius: 16px;
            padding: 50px;
            text-align: center;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }}
        .logo {{ font-size: 80px; margin-bottom: 20px; }}
        h1 {{ color: #3b82f6; margin-bottom: 20px; font-size: 28px; }}
        p {{ color: #a0a8c0; margin-bottom: 20px; }}
        .btn {{
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 14px 28px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
        }}
        .btn:hover {{ background: #60a5fa; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎵</div>
        <h1>Spotify</h1>
        <p>Lyssna på Spotify</p>
        <a href="{safe_url}" class="btn" target="_blank">Öppna i Spotify →</a>
    </div>
</body>
</html>
'''
    
    @staticmethod
    def _generate_tidal_player(url: str, title: str) -> str:
        """Generate Tidal player - direct link"""
        safe_url = url.replace('"', '&quot;')
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0a0e1a 0%, #1a2032 100%);
            color: #e8eaf0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 500px;
            background: #131824;
            border-radius: 16px;
            padding: 50px;
            text-align: center;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }}
        .logo {{ font-size: 80px; margin-bottom: 20px; }}
        h1 {{ color: #3b82f6; margin-bottom: 20px; font-size: 28px; }}
        p {{ color: #a0a8c0; margin-bottom: 20px; }}
        .btn {{
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 14px 28px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
        }}
        .btn:hover {{ background: #60a5fa; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎶</div>
        <h1>Tidal</h1>
        <p>Lyssna på Tidal</p>
        <a href="{safe_url}" class="btn" target="_blank">Öppna i Tidal →</a>
    </div>
</body>
</html>
'''
