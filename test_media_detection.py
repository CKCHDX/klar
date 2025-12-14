#!/usr/bin/env python3
"""
Test script to debug media detection in Klar
Run: python test_media_detection.py
"""

import sys
from pathlib import Path

print("=" * 60)
print("KLAR MEDIA DETECTION TEST")
print("=" * 60)

# Test imports
print("\n[1] Testing imports...")
try:
    from engine.video_support import VideoDetector, VideoType, VideoMetadata, VideoPlayer
    print("    ✅ video_support imported successfully")
except ImportError as e:
    print(f"    ❌ Failed to import video_support: {e}")
    sys.exit(1)

try:
    from engine.audio_support import AudioDetector, AudioType, AudioMetadata, AudioPlayer
    print("    ✅ audio_support imported successfully")
except ImportError as e:
    print(f"    ❌ Failed to import audio_support: {e}")
    sys.exit(1)

# Test video detection
print("\n[2] Testing VIDEO detection...")

test_videos = [
    ("https://www.svt.se/play/video/abc123", "SVT video (whitelisted)", VideoType.SVT, True),
    ("https://www.youtube.com/watch?v=xyz", "YouTube video (BLOCKED)", VideoType.BLOCKED, True),
    ("https://www.vimeo.com/123456", "Vimeo video (BLOCKED)", VideoType.BLOCKED, True),
    ("https://www.sverigesradio.se/media/audio.mp4", "MP4 on SR (whitelisted)", VideoType.HTML5_MP4, True),
]

for url, description, expected_type, should_detect in test_videos:
    is_video, vtype, vid = VideoDetector.detect_from_url(url)
    status = "✅" if (is_video == should_detect and vtype == expected_type) else "❌"
    print(f"    {status} {description}")
    print(f"       URL: {url}")
    print(f"       Expected: is_video={should_detect}, type={expected_type}")
    print(f"       Got: is_video={is_video}, type={vtype}")

# Test audio detection
print("\n[3] Testing AUDIO detection...")

test_audios = [
    ("https://www.sverigesradio.se/sida/1234", "SR audio (whitelisted)", AudioType.SR, True),
    ("https://open.spotify.com/track/123", "Spotify track (whitelisted)", AudioType.SPOTIFY, True),
    ("https://www.tidal.com/track/456", "Tidal track (whitelisted)", AudioType.TIDAL, True),
    ("https://music.youtube.com/watch?v=xyz", "YouTube Music (BLOCKED)", AudioType.BLOCKED, True),
    ("https://www.soundcloud.com/user/track", "SoundCloud (BLOCKED)", AudioType.BLOCKED, True),
    ("https://www.sverigesradio.se/audio/song.mp3", "MP3 on SR (whitelisted)", AudioType.HTML5_MP3, True),
]

for url, description, expected_type, should_detect in test_audios:
    is_audio, atype, aid = AudioDetector.detect_from_url(url)
    status = "✅" if (is_audio == should_detect and atype == expected_type) else "❌"
    print(f"    {status} {description}")
    print(f"       URL: {url}")
    print(f"       Expected: is_audio={should_detect}, type={expected_type}")
    print(f"       Got: is_audio={is_audio}, type={atype}")

# Test whitelist checking
print("\n[4] Testing WHITELIST checking...")

test_whitelist = [
    ("https://www.svt.se/play/video", "SVT (whitelisted)", True),
    ("https://www.sverigesradio.se/sida/1234", "SR (whitelisted)", True),
    ("https://open.spotify.com/track/123", "Spotify (whitelisted)", True),
    ("https://www.youtube.com/watch?v=xyz", "YouTube (NOT whitelisted)", False),
    ("https://www.netflix.com/watch", "Netflix (NOT whitelisted)", False),
]

for url, description, should_be_whitelisted in test_whitelist:
    is_whitelisted_v, domain_v = VideoDetector.is_whitelisted_domain(url)
    is_whitelisted_a, domain_a = AudioDetector.is_whitelisted_domain(url)
    is_whitelisted = is_whitelisted_v or is_whitelisted_a
    status = "✅" if is_whitelisted == should_be_whitelisted else "❌"
    print(f"    {status} {description}")
    print(f"       URL: {url}")
    print(f"       Expected: whitelisted={should_be_whitelisted}")
    print(f"       Got: whitelisted={is_whitelisted}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nIf all tests passed (✅), media detection is working correctly.")
print("If any tests failed (❌), check the console output above for details.")
print("\nNext step: Run 'python klar_browser.py' and test with real URLs")
