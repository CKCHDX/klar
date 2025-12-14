# Media Support Debugging Guide

## If Video/Audio Not Working

### Quick Checklist

1. **Check Console Output**
   ```bash
   python klar_browser.py
   ```
   Look for lines:
   - `[Media] Whitelisted-only media support enabled`
   - `[Video] Detected: ...` (when playing video)
   - `[Audio] Detected: ...` (when playing audio)

2. **Verify Files Exist**
   ```bash
   ls -la engine/video_support.py
   ls -la engine/audio_support.py
   ```
   Both files MUST exist

3. **Check Imports in klar_browser.py**
   Line ~33 should have:
   ```python
   from engine.video_support import VideoDetector, VideoPlayer, VideoMetadata, VideoType
   from engine.audio_support import AudioDetector, AudioPlayer, AudioMetadata, AudioType
   ```

4. **Check __init__.py**
   Should export audio and video classes

### Common Issues

#### Issue 1: ImportError for video_support or audio_support

**Symptom**: Python error when starting Klar
```
ModuleNotFoundError: No module named 'engine.video_support'
```

**Solution**:
1. Verify files exist: `engine/video_support.py` and `engine/audio_support.py`
2. Verify `engine/__init__.py` has proper imports
3. Restart Python/Klar

#### Issue 2: Media URL not detected

**Symptom**: Click SVT link, page loads normally instead of showing player

**Solution**:
1. Check console for `[Audio] Detected:` or `[Video] Detected:` message
2. If NOT detected, the URL pattern isn't matching
3. Add print statements in `AudioDetector.detect_from_url()` to debug

#### Issue 3: Player HTML generated but not displaying

**Symptom**: Console shows `[Audio] Playing:` but no player appears

**Solution**:
1. Check browser console (F12) for JavaScript errors
2. Verify HTML is valid
3. Check that `self.current_browser().setHtml()` is being called

### Manual Testing

**Test 1: SR Audio (Whitelisted)**
```
1. Run: python klar_browser.py
2. Enter: https://www.sverigesradio.se/sida/1234
3. Watch console for: [Audio] Detected: sr
4. Should show player or link
```

**Test 2: SVT Video (Whitelisted)**
```
1. Run: python klar_browser.py  
2. Enter: https://www.svt.se/play/video/abc123
3. Watch console for: [Video] Detected: svt
4. Should show player or link
```

**Test 3: YouTube (Should Block)**
```
1. Run: python klar_browser.py
2. Enter: https://www.youtube.com/watch?v=xyz
3. Should show block warning immediately
4. Should NOT attempt to play
```

### Enable Debug Logging

Edit `klar_browser.py`, find `check_media_url` method, add:

```python
def check_media_url(self, qurl: QUrl):
    """Audio and video detection - DEBUG VERSION"""
    url_string = qurl.toString()
    print(f"\n[DEBUG] check_media_url called with: {url_string}")
    
    # Check for audio first
    is_audio, audio_type, audio_id = AudioDetector.detect_from_url(url_string)
    print(f"[DEBUG] Audio detection result: is_audio={is_audio}, type={audio_type}")
    
    if is_audio:
        print(f"[Audio] Detected: {audio_type}")
        metadata = AudioMetadata(url_string)
        print(f"[DEBUG] Audio metadata: whitelisted={metadata.is_whitelisted}, can_play={metadata.can_play()}")
        # ... rest of method
    
    # Check for video if not audio
    is_video, video_type, video_id = VideoDetector.detect_from_url(url_string)
    print(f"[DEBUG] Video detection result: is_video={is_video}, type={video_type}")
    # ... rest of method
```

### Python Version

Ensure you're using Python 3.8+:
```bash
python --version
```

### PyQt6 Installation

Ensure PyQt6 and WebEngine are installed:
```bash
pip install PyQt6 PyQt6-WebEngine
```

### Check klar_browser.py is Updated

Make sure you have the LATEST version:
```bash
git pull
```

Should show commits like:
- "Integrate audio support into Klar browser"
- "Fix video support integration"

## Still Not Working?

Try this minimal test:

```python
# test_media.py
from engine.video_support import VideoDetector, VideoType
from engine.audio_support import AudioDetector, AudioType

# Test video detection
url = "https://www.svt.se/play/video/abc123"
is_video, vtype, vid = VideoDetector.detect_from_url(url)
print(f"Video: {is_video}, Type: {vtype}")

# Test audio detection  
url2 = "https://www.sverigesradio.se/sida/1234"
is_audio, atype, aid = AudioDetector.detect_from_url(url2)
print(f"Audio: {is_audio}, Type: {atype}")

# Test blocking
url3 = "https://www.youtube.com/watch?v=xyz"
is_video3, vtype3, vid3 = VideoDetector.detect_from_url(url3)
print(f"YouTube blocked: {vtype3 == VideoType.BLOCKED}")
```

Run: `python test_media.py`

Should output:
```
Video: True, Type: VideoType.SVT
Audio: True, Type: AudioType.SR
YouTube blocked: True
```

If not, the detection logic has an issue.

## Report Format

If still stuck, include:
1. **Console output** (first 50 lines)
2. **URL you tested** (e.g., `https://www.svt.se/play/...`)
3. **What happened** (page loaded normally, error, blank page, etc.)
4. **Python version** (`python --version`)
5. **PyQt6 version** (`pip show PyQt6`)
6. **File list** (`ls -la engine/*.py | grep -E 'video|audio'`)
