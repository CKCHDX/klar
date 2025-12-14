# Klar Video Support - Swedish Whitelisted Domains Only

**STATUS**: ✅ Video support respects Klar's whitelisted-only policy

## What Is Klar?

Klar is a **Swedish-only search engine** focusing on:
- 🇬🇮 **Swedish content only** - indexed from whitelisted Swedish domains
- 🔐 **Security-first** - no external domains, no YouTube, no global services
- 🔍 **Privacy** - GDPR compliant, no tracking
- ⚡ **Speed** - optimized for Swedish users searching Swedish content

**Klar does NOT allow access to external domains.** Your browser instance is restricted to only whitelisted Swedish websites.

## Video Support Philosophy

Klar's video support follows the same principle:

### ❌ What Video Support DOES NOT Do
- ❌ Does NOT support YouTube
- ❌ Does NOT support Vimeo, Dailymotion, or other external services
- ❌ Does NOT embed players from non-whitelisted domains
- ❌ Does NOT access external streaming platforms

### ✅ What Video Support DOES Do
- ✅ Plays videos from **whitelisted Swedish domains only**
- ✅ Supports SVT (Swedish Television), SR, UR, Filmstaden
- ✅ Plays direct video files (.mp4, .webm) hosted on whitelisted domains
- ✅ Supports HLS/DASH streams from whitelisted sources
- ✅ Blocks videos from non-whitelisted domains automatically

## Supported Sources

### Swedish Public Broadcasters (Whitelisted)

| Service | Domain | Type | Support |
|---------|--------|------|----------|
| **SVT** (Swedish Television) | svt.se | Streaming | Direct link |
| **SR** (Sveriges Radio) | sverigesradio.se | Audio/Video | Direct link |
| **UR** (Educational) | ur.se | Educational | Direct link |
| **Filmstaden** (Cinema) | filmstaden.se | Movies | Direct link |
| **Blockflix** (Streaming) | blockflix.se | Streaming | Direct link* |

*If added to domains.json

### Direct File Support (On Whitelisted Domains)

| Format | Extension | Support | Example |
|--------|-----------|---------|----------|
| **MP4** | .mp4 | ✅ Full | svt.se/media/video.mp4 |
| **WebM** | .webm | ✅ Full | ur.se/stream.webm |
| **OGV** | .ogv | ✅ Full | example.se/video.ogv |
| **HLS** | .m3u8 | ✅ Full | sr.se/stream/live.m3u8 |
| **DASH** | .mpd | ✅ Full | svt.se/stream/dash.mpd |

## Architecture

### Security: Whitelisted-Only Design

```
User enters URL
    ↓
Check against domains.json whitelist
    ├─ Domain whitelisted? → YES → Continue
    └─ Domain NOT whitelisted? → NO → Block with warning
         ↓
Detect if content is video
    ├─ SVT video → Generate player
    ├─ Direct MP4 → Generate player
    ├─ HLS stream → Generate player
    └─ Not a video → Load normally
         ↓
Generate appropriate player
```

### Components

#### `VideoDetector`
Detects video content from whitelisted domain URLs only:
```python
is_whitelisted, domain = VideoDetector.is_whitelisted_domain(url)
if not is_whitelisted:
    # Block with warning
else:
    is_video, video_type, video_id = VideoDetector.detect_from_url(url)
```

**Detects:**
- SVT Play videos (svt.se)
- Sveriges Radio content (sverigesradio.se)
- UR Educational content (ur.se)
- Filmstaden movies (filmstaden.se)
- Direct video files (.mp4, .webm, .m3u8, etc.)

#### `VideoMetadata`
Extracts metadata from whitelisted videos:
```python
metadata = VideoMetadata(url)  # Only works if whitelisted
if metadata.is_whitelisted and metadata.can_play():
    # Generate player
```

#### `VideoPlayer`
Generates HTML for playback:
```python
# Whitelisted Swedish services
html = VideoPlayer.generate_player_html(url, VideoType.SVT, title)

# Direct files
html = VideoPlayer.generate_player_html(url, VideoType.HTML5_MP4, title)
```

## Usage Examples

### Example 1: SVT Video (Whitelisted)

```
User visits: https://www.svt.se/play/video
         ↓
Detector: Domain is svt.se (whitelisted) ✓
         ↓
Detector: Content is video (SVT format) ✓
         ↓
Player: Opens SVT player button
```

### Example 2: Direct MP4 on SR (Whitelisted)

```
User visits: https://www.sverigesradio.se/media/audio.mp4
         ↓
Detector: Domain is sverigesradio.se (whitelisted) ✓
         ↓
Detector: Content is MP4 video file ✓
         ↓
Player: Shows HTML5 video player with controls
```

### Example 3: YouTube Video (NOT Whitelisted) - BLOCKED

```
User tries: https://www.youtube.com/watch?v=...
         ↓
Detector: Domain is youtube.com (NOT in domains.json) ✗
         ↓
Block: Shows security warning
       "Video from this domain is blocked"
       "Only approved Swedish sources allowed"
```

## Adding Video Support to Whitelisted Domains

If a whitelisted domain (in domains.json) hosts videos, **no code changes needed**! Video support automatically:

1. Detects direct video files (.mp4, .webm, .m3u8)
2. Generates HTML5 player
3. Works immediately

### To Add a New Swedish Service

Example: Adding Vimeo Sweden (if it were added to domains.json):

1. **Add domain** to `domains.json`
2. **Update VideoDetector**:
   ```python
   if 'vimeo-se.com' in url_lower:
       # Detect Vimeo Sweden content
   ```
3. **Add VideoType**:
   ```python
   VIMEO_SWEDEN = "vimeo_se"
   ```
4. **Add player generation**:
   ```python
   @staticmethod
   def _generate_vimeo_sweden_player(url, title):
       # Generate player
   ```

## Integration with Klar Browser

### In `klar_browser.py`

```python
from engine.video_support import VideoDetector, VideoPlayer, VideoMetadata
from engine.domain_whitelist import DomainWhitelist

def check_video_url(self, qurl: QUrl):
    """Check for video and validate against whitelist"""
    url_string = qurl.toString()
    
    # Check whitelist first (security!)
    is_whitelisted, reason = self.domain_whitelist.is_whitelisted(url_string)
    if not is_whitelisted:
        # Block with warning
        self.display_blocked_page(reason)
        return
    
    # Detect video on whitelisted domain
    is_video, video_type, video_id = VideoDetector.detect_from_url(url_string)
    if is_video:
        metadata = VideoMetadata(url_string)
        if metadata.can_play():
            html = VideoPlayer.generate_player_html(
                url_string, video_type, metadata.title
            )
            self.load_html(html)
```

## Security Features

### 1. Whitelist-First Design
- ✅ EVERY URL checked against domains.json first
- ✅ Non-whitelisted domains BLOCKED immediately
- ✅ No exceptions, no override

### 2. Video Type Validation
- ✅ Only known video types allowed
- ✅ No arbitrary file downloads
- ✅ MIME type verification

### 3. HTML Sanitization
- ✅ All URLs escaped for HTML context
- ✅ XSS prevention on metadata display
- ✅ No user input in HTML generation

### 4. Player Isolation
- ✅ No cookies shared with videos
- ✅ No cross-domain access
- ✅ No plugins or extensions

## User Experience

### Allowed Videos (Whitelisted Domain)
```
User tries to play SVT video
       ↓
✓ Whitelist check passes
       ↓
✓ Video detected
       ↓
✓ Player appears
       ↓
User watches content
```

### Blocked Videos (Non-Whitelisted Domain)
```
User tries to play YouTube video
       ↓
✗ Whitelist check fails
       ↓
Warning message appears:
"Video från denna domän är blockerad"
(Video from this domain is blocked)

"Endast godkända svenska domäner tillåtna"
(Only approved Swedish domains allowed)
```

## Whitelisted Domains with Video Content

Current domains.json includes:
- ✅ svt.se - SVT Play
- ✅ sverigesradio.se - SR
- ✅ ur.se - UR Educational
- ✅ filmstaden.se - Filmstaden Cinema
- ✅ spotify.com - Music streaming* (*audio, not video)
- ✅ tidal.com - Music streaming* (*audio, not video)

Plus 110+ other Swedish government, news, education, and business sites.

## Troubleshooting

### Issue: "Video from this domain is blocked"

**Reason**: The domain is not in domains.json (Klar's whitelist)

**Solution**: 
- Contact oscyra.solutions
- Provide Swedish domain name
- Request domain to be added to whitelist

### Issue: Video file shows but doesn't play

**Possible reasons**:
1. Browser doesn't support format (.ogv rarely works)
2. Video URL is incorrect
3. Video file is missing/moved

**Solution**:
- Try different format (MP4 most compatible)
- Check URL is correct
- Verify on original website

### Issue: SVT video doesn't play directly

**Reason**: SVT requires clicking through to their player

**Solution**: This is expected - Klar shows a button to open SVT's official player

## Performance

- **Whitelist check**: <1ms per URL
- **Video detection**: <1ms per URL
- **Player generation**: <1ms HTML string building
- **Total overhead**: Negligible

## Future Enhancements

When/if new whitelisted domains are added:
- [ ] Support for more Swedish streaming services
- [ ] Playlist detection and support
- [ ] Subtitle support from whitelisted sources
- [ ] Quality selection for HLS/DASH
- [ ] Viewing statistics in LOKI cache

## Resources

- **Klar Philosophy**: README.md
- **Domain Whitelist**: domains.json
- **Whitelist Implementation**: engine/domain_whitelist.py
- **Video Support Code**: engine/video_support.py

## Contact

For questions about video support or to request whitelisted domains:
- Website: https://oscyra.solutions/
- Project: https://github.com/CKCHDX/klar

---

**Klar Video Support respects Swedish privacy, security, and focus.** Only whitelisted domains. Only Swedish content. No exceptions.
