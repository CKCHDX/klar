# Klar Video Support - Quick Reference

## TL;DR

**Klar is a Swedish-only search engine. Video support respects this.**

### ✅ Works (Whitelisted Domains)
- SVT videos (svt.se)
- SR videos (sverigesradio.se)
- UR videos (ur.se)
- Filmstaden videos (filmstaden.se)
- Any .mp4 on a whitelisted domain
- Any .m3u8 (HLS stream) on a whitelisted domain

### ❌ Doesn't Work (Non-Whitelisted)
- YouTube ✗
- Vimeo ✗
- TikTok ✗
- Instagram ✗
- Any non-whitelisted domain ✗

## How It Works

```
User enters URL
  ↓
Is domain in domains.json?
  ├─ YES → Check for video
  └─ NO  → BLOCK (🔒)
```

## Code Integration

```python
from engine.video_support import VideoDetector, VideoPlayer, VideoMetadata

# Check URL
url = "https://www.svt.se/play/video"

# Detect video
is_video, video_type, video_id = VideoDetector.detect_from_url(url)

if is_video:
    metadata = VideoMetadata(url)
    if metadata.can_play():
        html = VideoPlayer.generate_player_html(
            url, video_type, metadata.title
        )
        # Display HTML player
```

## Supported Video Types

| Type | Extension | Status |
|------|-----------|--------|
| MPEG4 | .mp4 | ✅ |
| WebM | .webm | ✅ |
| OGG | .ogv | ✅ |
| HLS | .m3u8 | ✅ |
| DASH | .mpd | ✅ |
| SVT | svt.se | ✅ |
| SR | sverigesradio.se | ✅ |
| UR | ur.se | ✅ |
| Filmstaden | filmstaden.se | ✅ |

## For Developers

### Check if domain is whitelisted
```python
is_whitelisted, domain = VideoDetector.is_whitelisted_domain(url)
```

### Detect video type
```python
is_video, vtype, vid = VideoDetector.detect_from_url(url)
# Returns: (bool, VideoType, str)
```

### Generate player
```python
html = VideoPlayer.generate_player_html(
    url=url,
    video_type=vtype,
    title="My Video"
)
```

## Adding New Domains

### If domain is already in domains.json
**Automatic!** Just add videos to the domain:
- `newdomain.se/video.mp4` → Works immediately
- No code changes needed

### If domain not in domains.json
1. Add to `domains.json`
2. Update `VideoDetector.WHITELISTED_DOMAINS` (optional)
3. Add detection logic if needed
4. Done!

## Security Rules

1. 🔐 **Whitelist-First**: Every URL checked first
2. 🔐 **No Exceptions**: Non-whitelisted = blocked
3. 🔐 **Sanitized**: All HTML escaped
4. 🔐 **Swedish-Only**: No external services

## User Messages (Swedish)

### Blocked Domain
```
🔒 Video från denna domän är blockerad

Endast godkända svenska domäner tillåtna.
```

### Allowed Domain
```
✓ Godkänd svensk källa
```

## Testing Examples

### Test 1: Whitelisted Video
```
URL: https://www.svt.se/play/video/video-id
Expected: Player appears
Result: ??? TEST IT
```

### Test 2: Blocked Video
```
URL: https://www.youtube.com/watch?v=xyz
Expected: Block warning
Result: ??? TEST IT
```

### Test 3: MP4 on Whitelisted
```
URL: https://www.sverigesradio.se/media.mp4
Expected: HTML5 player
Result: ??? TEST IT
```

## Files

- `engine/video_support.py` - Core implementation
- `engine/__init__.py` - Package exports
- `README_VIDEO_SUPPORT.md` - Full documentation
- `VIDEO_SUPPORT_WHITELIST_ONLY.md` - Design rationale
- `QUICK_REFERENCE_VIDEO.md` - This file

## Remember

✅ **Only whitelisted domains**  
✅ **Only Swedish sources**  
✅ **Only approved video types**  
✅ **Always check domains.json**  

---

For details, see: `README_VIDEO_SUPPORT.md` and `VIDEO_SUPPORT_WHITELIST_ONLY.md`
