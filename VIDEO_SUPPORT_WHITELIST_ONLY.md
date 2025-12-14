# Klar Video Support - Whitelisted-Only Implementation

**Date**: December 14, 2025  
**Status**: ✅ CORRECTED - Now respects Klar's security policy

## The Problem With Initial Implementation

The original video support module was designed like a general browser:
- ❌ Supported YouTube, Vimeo, TikTok, etc.
- ❌ No domain validation
- ❌ Violated Klar's Swedish-only, whitelisted-only principle

**This was WRONG for Klar.**

## What Changed

### Understanding Klar

Klar is NOT a general web browser. It's a **Swedish search engine** with **strict security**:

```
Klar Design Philosophy:

Input URL
  ↓
Check against domains.json (whitelist)
  ├─ Whitelisted? → ALLOW
  └─ Not whitelisted? → BLOCK
  ↓
Process content
(search, show page, etc.)
```

Every single URL goes through this security check first.

### Video Support Must Follow Same Pattern

**OLD (WRONG):**
```
Detect video from ANY source
  ↓
Generate player
  ↓
User watches
```

**NEW (CORRECT):**
```
Check if domain is whitelisted
  ├─ Not whitelisted? → BLOCK
  └─ Whitelisted? ↓
Detect video
  ↓
Generate player
  ↓
User watches
```

## Implementation Details

### Modified: `engine/video_support.py`

**Key Changes:**

1. **Whitelist Check First**
```python
is_whitelisted, domain = VideoDetector.is_whitelisted_domain(url)
if not is_whitelisted:
    return False, VideoType.BLOCKED, None  # BLOCK immediately
```

2. **Limited Service Support**
```python
# OLD: YouTube, Vimeo, TikTok, Instagram, etc.

# NEW: Only Swedish whitelisted sources
WHITELISTED_DOMAINS = {
    'svt.se': 'SVT (Swedish Television)',
    'sverigesradio.se': 'SR (Sveriges Radio)',
    'ur.se': 'UR (Educational)',
    'filmstaden.se': 'Filmstaden (Cinema)',
}
```

3. **Blocked Domain Handling**
```python
if video_type == VideoType.BLOCKED:
    return VideoPlayer._generate_blocked_html(url)
    # Shows user-friendly warning in Swedish
```

4. **Swedish User Messages**
```
Vidoe från denna domän är blockerad
(Video from this domain is blocked)

Endast godkända svenska domäner tillåtna
(Only approved Swedish domains allowed)
```

### Supported Video Sources (Whitelisted Only)

| Source | Domain | Type | Status |
|--------|--------|------|--------|
| SVT | svt.se | Videos | ✅ |
| SR | sverigesradio.se | Audio/Video | ✅ |
| UR | ur.se | Educational | ✅ |
| Filmstaden | filmstaden.se | Movies | ✅ |
| **Any .mp4 on whitelist** | *.se | Direct file | ✅ |
| **Any .m3u8 on whitelist** | *.se | HLS stream | ✅ |
| **YouTube** | youtube.com | - | ❌ BLOCKED |
| **Vimeo** | vimeo.com | - | ❌ BLOCKED |
| **TikTok** | tiktok.com | - | ❌ BLOCKED |
| **Any other site** | *.com | - | ❌ BLOCKED |

## How It Works

### Scenario 1: User tries to watch SVT (Whitelisted)

```
URL: https://www.svt.se/play/video/abc123
  ↓
Whitelist check: svt.se is in domains.json ✓
  ↓
Video detection: SVT format detected ✓
  ↓
Player generation: SVT player HTML generated
  ↓
Result: User can watch SVT content
```

### Scenario 2: User tries to watch YouTube (NOT Whitelisted)

```
URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
  ↓
Whitelist check: youtube.com is NOT in domains.json ✗
  ↓
Blocked: VideoType.BLOCKED returned
  ↓
Warning page shown:
  🔒 "Video från denna domän är blockerad"
  "Endast godkända svenska domäner tillåtna"
  ↓
Result: User cannot watch YouTube
```

### Scenario 3: User tries to watch MP4 on SR (Whitelisted)

```
URL: https://www.sverigesradio.se/media/audio.mp4
  ↓
Whitelist check: sverigesradio.se is in domains.json ✓
  ↓
Video detection: .mp4 file detected ✓
  ↓
Player generation: HTML5 video player
  ↓
Result: User sees HTML5 player with controls
```

## Adding New Domains with Video Content

### If a domain is already whitelisted (in domains.json)

**Direct video files work automatically!**

Example: If `example.se` is added to domains.json and has an `example.se/video.mp4` URL:

1. Whitelist check passes ✓
2. Video detector finds `.mp4` extension ✓
3. HTML5 player generated automatically ✓
4. **No code changes needed!**

### To add support for a new Swedish streaming service

1. **Add domain to domains.json** (e.g., "newstreaming.se")

2. **Update VideoDetector.WHITELISTED_DOMAINS** in `engine/video_support.py`:
```python
WHITELISTED_DOMAINS = {
    'svt.se': 'SVT',
    'newstreaming.se': 'New Swedish Service',  # ADD THIS
    # ...
}
```

3. **Add detection logic** in `detect_from_url()`:
```python
if 'newstreaming.se' in url_lower:
    # Detect video IDs or patterns
    return True, VideoType.NEW_SERVICE, video_id
```

4. **Add VideoType enum value**:
```python
class VideoType(Enum):
    NEW_SERVICE = "new_service"  # ADD THIS
```

5. **Add player generation method**:
```python
@staticmethod
def _generate_new_service_player(url, title):
    # Generate HTML for player
```

## Security Model

### Principle 1: Whitelist-First
- Every URL validated against domains.json
- No URL bypasses this check
- Non-whitelisted domains ALWAYS blocked

### Principle 2: Known Video Types Only
- Only approved video formats handled
- Unknown formats rejected
- Extensions validated (.mp4, .webm, .m3u8 only)

### Principle 3: HTML Sanitization
- All URLs escaped for HTML display
- No user input in generated HTML
- XSS prevention on all metadata

### Principle 4: Swedish-Only Content
- No external services embedded
- Only whitelisted Swedish domains
- Respects Klar's privacy-first design

## User Experience

### For Allowed Content (Whitelisted)
```
✅ Player appears
✅ Full controls available
✅ Seamless playback
✅ Swedish UI (if applicable)
```

### For Blocked Content (Non-Whitelisted)
```
✗ Blocked warning appears
🔒 Explains domain restriction
🇬🇮 States "only Swedish domains"
📌 Contact info for requests
```

## Integration in klar_browser.py

The video support integrates seamlessly with existing Klar flow:

```python
# 1. User navigates to URL
self.navigate(qurl)

# 2. Domain whitelist checks (existing code)
is_whitelisted, reason = self.domain_whitelist.is_whitelisted(url)
if not is_whitelisted:
    self.load_html(blocked_page)
    return

# 3. Check for video (NEW)
is_video, video_type, video_id = VideoDetector.detect_from_url(url)
if is_video:
    metadata = VideoMetadata(url)
    if metadata.can_play():
        html = VideoPlayer.generate_player_html(url, video_type, metadata.title)
        self.load_html(html)

# 4. Load page normally (existing)
self.web_view.setUrl(qurl)
```

## What Happens with Different URLs

### svt.se/play/video (SVT - Whitelisted)
```
✅ Whitelisted? YES (svt.se in domains.json)
✅ Video detected? YES (SVT format)
✅ Result: SVT player shown
```

### sverigesradio.se/video.mp4 (SR - Whitelisted)
```
✅ Whitelisted? YES (sverigesradio.se in domains.json)
✅ Video detected? YES (.mp4 file)
✅ Result: HTML5 player shown
```

### youtube.com/watch?v=... (YouTube - NOT Whitelisted)
```
✗ Whitelisted? NO (youtube.com NOT in domains.json)
✗ Result: BLOCKED immediately, warning shown
         (Never even checks for video!)
```

### netflix.com/watch/... (Netflix - NOT Whitelisted)
```
✗ Whitelisted? NO (netflix.com NOT in domains.json)
✗ Result: BLOCKED immediately
```

### example.se/video.mp4 (Generic Swedish - Whitelisted)
```
✅ Whitelisted? YES (assuming in domains.json)
✅ Video detected? YES (.mp4 file)
✅ Result: HTML5 player shown
```

## Advantages of This Design

### Security
- 🔐 No external services can be accessed
- 🔐 Malicious sites cannot bypass whitelist
- 🔐 Users protected from phishing/scams

### Privacy
- 🔕 No data sent to YouTube/TikTok/etc.
- 🔕 No tracking by external services
- 🔕 GDPR compliant

### Simplicity
- 🌟 Clear rules: whitelist = allowed, non-whitelist = blocked
- 🌟 Users understand the limitation
- 🌟 Developers understand the policy

### Extensibility
- 🔧 Easy to add new whitelisted domains
- 🔧 Automatic video file support (.mp4, .webm, etc.)
- 🔧 New services just need domain + detection logic

## Testing Checklist

- [ ] SVT video plays (whitelisted)
- [ ] SR video plays (whitelisted)
- [ ] YouTube shows block warning (not whitelisted)
- [ ] Vimeo shows block warning (not whitelisted)
- [ ] Netflix shows block warning (not whitelisted)
- [ ] Direct MP4 on whitelisted domain plays
- [ ] Direct MP4 on non-whitelisted domain blocked
- [ ] HLS stream on whitelisted domain works
- [ ] Warning message displays correctly
- [ ] No exceptions to whitelist

## File Changes Summary

**Updated**: `engine/video_support.py`
- Removed support for YouTube, Vimeo, TikTok, etc.
- Added whitelist validation
- Refactored for whitelisted-only operation
- Swedish user messages
- Blocked domain handling

**Updated**: `README_VIDEO_SUPPORT.md`
- New documentation explaining whitelisted-only policy
- Examples of allowed/blocked scenarios
- Security model explanation

**New**: `VIDEO_SUPPORT_WHITELIST_ONLY.md` (this file)
- Design rationale
- Implementation details
- Integration guide
- Testing checklist

## Conclusion

Klar's video support now:

✅ **Respects Klar's whitelisted-only principle**  
✅ **Blocks all non-whitelisted domains**  
✅ **Plays videos from Swedish whitelisted sources only**  
✅ **Maintains security and privacy**  
✅ **Works seamlessly with existing Klar architecture**  

This is how Klar should handle video - with the same strict security it applies to everything else.

---

**Klar: Clear, Fast, Secure Search - For Sweden, By Sweden**
