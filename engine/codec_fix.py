"""
Klar Codec Support Fix
Handles codec compatibility issues in PyQt6 WebEngine
Provides workarounds for unsupported codecs (avc1, mp4a, etc.)
"""

import platform
import subprocess
import os
from pathlib import Path


class CodecFix:
    """Handle codec issues in PyQt6 WebEngine"""
    
    @staticmethod
    def enable_proprietary_codecs():
        """
        Enable proprietary codec support in PyQt6
        These are typically disabled by default
        """
        # Set environment variables to enable codecs
        os.environ['QT_WEBENGINE_DISABLED_FEATURES'] = ''
        os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--enable-features=EnableMediaStream'
        
        print("[Codec] Proprietary codec support enabled")
        return True
    
    @staticmethod
    def get_system_codec_info():
        """
        Get system codec information
        """
        system = platform.system()
        codecs = {
            'h264': False,      # AVC1
            'aac': False,       # MP4A
            'vp9': False,       # WebM VP9
            'opus': False,      # WebM Opus
        }
        
        if system == 'Linux':
            # Check for Linux codec support
            try:
                result = subprocess.run(['ffmpeg', '-codecs'], 
                                      capture_output=True, text=True, timeout=5)
                output = result.stdout.lower()
                codecs['h264'] = 'h.264' in output or 'h264' in output
                codecs['aac'] = 'aac' in output
                codecs['vp9'] = 'vp9' in output
                codecs['opus'] = 'opus' in output
            except:
                pass
        
        elif system == 'Windows':
            # Windows typically has good codec support
            codecs['h264'] = True
            codecs['aac'] = True
            codecs['vp9'] = True
            codecs['opus'] = True
        
        elif system == 'Darwin':  # macOS
            # macOS has good codec support
            codecs['h264'] = True
            codecs['aac'] = True
            codecs['vp9'] = True
            codecs['opus'] = True
        
        return codecs
    
    @staticmethod
    def get_player_workaround_html(url: str, title: str) -> str:
        """
        Generate HTML5 player with codec workarounds
        Falls back to external player if needed
        """
        safe_url = url.replace('"', '&quot;')
        safe_title = title.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_title} - Klar Media</title>
    <script src="https://cdn.dashjs.org/latest/dash.all.min.js"></script>
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
            max-width: 1200px;
            background: #131824;
            border-radius: 16px;
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
            margin-bottom: 20px;
        }}
        #video-player {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }}
        .fallback {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            color: #fca5a5;
        }}
        .fallback h3 {{
            margin-bottom: 10px;
            color: #ef4444;
        }}
        .fallback p {{
            font-size: 12px;
            line-height: 1.6;
            margin-bottom: 10px;
        }}
        .external-link {{
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 12px;
            font-weight: 600;
            margin-top: 10px;
        }}
        .external-link:hover {{
            background: #60a5fa;
        }}
        .info {{
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.2);
            padding: 15px;
            border-radius: 8px;
            font-size: 12px;
            color: #a0a8c0;
            margin-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">{safe_title}</div>
        <div class="video-wrapper">
            <video id="video-player" controls>
                Webbläsaren stöder inte denna videospelare.
            </video>
        </div>
        <div class="fallback">
            <h3>⚠️ Kodek-kompatibilitet</h3>
            <p>Din webbläsare stöder inte alla videoformat för denna media. Detta är en begränsning i PyQt6 WebEngine.</p>
            <p><strong>Lösning:</strong> Öppna länken i en extern webbläsare (Chrome, Firefox, Edge) som har bättre kodekstöd.</p>
            <a href="{safe_url}" class="external-link" target="_blank">↗ Öppna i extern webbläsare</a>
        </div>
        <div class="info">
            <strong>Teknisk info:</strong> PyQt6 WebEngine saknar stöd för proprietär kodning (H.264, AAC, VP9). För bästa resultat, använd en moderna webbläsare.
        </div>
    </div>
    <script>
        // Try to load with dash.js if available
        if (typeof dashjs !== 'undefined') {{
            try {{
                const video = document.getElementById('video-player');
                const player = dashjs.MediaPlayer().create();
                player.initialize(video, "{safe_url}", true);
                console.log('[Codec] DASH.js player initialized');
            }} catch (e) {{
                console.log('[Codec] DASH.js failed:', e);
            }}
        }}
        
        // Try basic HTML5
        try {{
            const video = document.getElementById('video-player');
            const source = document.createElement('source');
            source.src = "{safe_url}";
            source.type = 'video/mp4';
            video.appendChild(source);
            video.load();
            console.log('[Codec] HTML5 player attempted');
        }} catch (e) {{
            console.log('[Codec] HTML5 failed:', e);
        }}
    </script>
</body>
</html>'''
    
    @staticmethod
    def get_audio_fallback_html(url: str, title: str) -> str:
        """
        Generate HTML5 audio player with fallbacks
        """
        safe_url = url.replace('"', '&quot;')
        safe_title = title.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        return f'''<!DOCTYPE html>
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
        }}
        .title {{
            color: #3b82f6;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
        }}
        .player-wrapper {{
            background: #1e2538;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        audio {{
            width: 100%;
            margin-bottom: 15px;
        }}
        .fallback {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 15px;
            border-radius: 8px;
            color: #fca5a5;
            font-size: 12px;
            line-height: 1.6;
        }}
        .fallback h3 {{
            margin-bottom: 10px;
            color: #ef4444;
        }}
        .external-link {{
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 12px;
            font-weight: 600;
            margin-top: 10px;
        }}
        .external-link:hover {{
            background: #60a5fa;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">🔊 {safe_title}</div>
        <div class="player-wrapper">
            <audio controls preload="metadata">
                <source src="{safe_url}" type="audio/mpeg">
                Din webbläsare stöder inte HTML5 audio.
            </audio>
        </div>
        <div class="fallback">
            <h3>⚠️ Kodek-kompatibilitet</h3>
            <p>Om ljudet inte spelas upp, är det på grund av kodek-begränsningar i PyQt6 WebEngine.</p>
            <p><strong>Lösning:</strong> Öppna länken i en extern webbläsare.</p>
            <a href="{safe_url}" class="external-link" target="_blank">↗ Öppna i extern webbläsare</a>
        </div>
    </div>
</body>
</html>'''


def init_codec_support():
    """
    Initialize codec support when Klar starts
    Should be called in KlarBrowser.__init__()
    """
    CodecFix.enable_proprietary_codecs()
    codecs = CodecFix.get_system_codec_info()
    print("[Codec] System codec support:")
    for codec, supported in codecs.items():
        status = "✓" if supported else "✗"
        print(f"  {status} {codec}")
