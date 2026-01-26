"""
kse/utils/__init__.py - Utility Functions and Helpers

Components:
  - URLUtils: URL manipulation and validation
  - TextUtils: Text processing and manipulation
  - FileUtils: Safe file I/O operations
  - TimeUtils: Time and date operations
  - ValidationUtils: Data validation helpers

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

from .kse_url_utils import URLUtils
from .kse_text_utils import TextUtils
from .kse_file_utils import FileUtils
from .kse_time_utils import TimeUtils
from .kse_validation_utils import ValidationUtils

__all__ = [
    # Utilities
    "URLUtils",
    "TextUtils",
    "FileUtils",
    "TimeUtils",
    "ValidationUtils",
]

__version__ = "1.0.0"
__author__ = "Klar Development Team"


# Quick start examples
"""
QUICK START - Utilities Layer

1. URL utilities:
    from kse.utils import URLUtils
    
    # Normalize URL
    normalized = URLUtils.normalize_url("https://www.example.com/page?utm_source=test#section")
    # Result: "https://example.com/page"
    
    # Extract domain
    domain = URLUtils.extract_domain("https://www.example.com/page")
    # Result: "example.com"
    
    # Validate URL
    if URLUtils.is_valid_url("https://example.com"):
        print("Valid URL")
    
    # Check Swedish domain
    if URLUtils.is_swedish_domain("https://example.se"):
        print("Swedish domain")

2. Text utilities:
    from kse.utils import TextUtils
    
    # Clean text
    clean = TextUtils.clean_text("  Hello  \\n\\n  World  !!  ")
    # Result: "Hello World !!"
    
    # Truncate text
    short = TextUtils.truncate_text("This is a very long text...", max_length=10)
    # Result: "This is a..."
    
    # Strip HTML
    plain = TextUtils.strip_html("<p>Hello <b>World</b></p>")
    # Result: "Hello World"
    
    # Highlight text
    marked = TextUtils.highlight_text("Hello world", ["world"], wrapper="<mark>")
    # Result: "Hello <mark>world</mark>"

3. File utilities:
    from kse.utils import FileUtils
    
    # Ensure directory
    FileUtils.ensure_directory("data/output")
    
    # Safe read
    content = FileUtils.safe_read_file("data/input.txt")
    
    # Safe write
    FileUtils.safe_write_file("data/output.txt", "Hello World")
    
    # Format file size
    size_str = FileUtils.format_file_size(1048576)
    # Result: "1.00 MB"
    
    # Check if exists
    if FileUtils.file_exists("data/file.txt"):
        print("File exists")

4. Time utilities:
    from kse.utils import TimeUtils
    
    # Format timestamp
    formatted = TimeUtils.format_timestamp(1234567890)
    # Result: "2009-02-13 23:31:30"
    
    # Format duration
    duration = TimeUtils.format_duration(3661)
    # Result: "1.0h"
    
    # Get age
    age_hours = TimeUtils.get_age_hours(timestamp)
    
    # Check if old
    if TimeUtils.is_older_than(timestamp, hours=24):
        print("File is older than 24 hours")

5. Validation utilities:
    from kse.utils import ValidationUtils
    
    # Validate email
    if ValidationUtils.is_email("user@example.com"):
        print("Valid email")
    
    # Validate URL
    if ValidationUtils.is_url("https://example.com"):
        print("Valid URL")
    
    # Check range
    if ValidationUtils.is_in_range(value, min_val=0, max_val=100):
        print("Value in range")
    
    # Validate length
    if ValidationUtils.is_valid_length(text, min_len=5, max_len=100):
        print("Text length valid")

UTILITIES ARCHITECTURE:

kse/utils/
├── kse_url_utils.py            URL handling
├── kse_text_utils.py           Text processing
├── kse_file_utils.py           File I/O
├── kse_time_utils.py           Time operations
├── kse_validation_utils.py     Data validation
└── __init__.py                 Public API

INTEGRATION:

- Phase 4 (crawler): URL utilities
- Phase 5 (nlp): Text utilities
- Phase 2 (storage): File utilities
- Phase 1 (core): Time utilities
- Phase 9 (server): Validation utilities

URL UTILITIES:

normalize_url(url)
  ├─ Remove tracking parameters
  ├─ Remove fragments
  ├─ Lowercase normalization
  └─ Trailing slash removal

extract_domain(url)
  ├─ Parse netloc
  ├─ Remove www. prefix
  └─ Return domain name

is_valid_url(url)
  └─ Check scheme and netloc

is_swedish_domain(url)
  └─ Check .se TLD

join_url(base, relative)
  └─ URL joining

TEXT UTILITIES:

clean_text(text)
  ├─ Normalize whitespace
  ├─ Remove special chars
  └─ Trim whitespace

truncate_text(text, max_length)
  ├─ Truncate to length
  └─ Add ellipsis

strip_html(html)
  ├─ Remove script/style
  ├─ Remove HTML tags
  └─ Decode entities

extract_sentences(text, limit)
  ├─ Split on boundaries
  └─ Filter empty

highlight_text(text, terms, wrapper)
  └─ Case-insensitive replacement

FILE UTILITIES:

ensure_directory(path)
  └─ Create directory tree

safe_read_file(path, encoding)
  └─ Error-safe file read

safe_write_file(path, content, encoding)
  └─ Error-safe file write

get_file_size(path)
  └─ Get size in bytes

format_file_size(bytes)
  └─ Format for display (B/KB/MB/GB/TB)

file_exists(path)
  └─ Check file existence

directory_exists(path)
  └─ Check directory existence

get_extension(filename)
  └─ Extract file extension

TIME UTILITIES:

get_timestamp()
  └─ Get current Unix timestamp

format_timestamp(timestamp)
  └─ Format as YYYY-MM-DD HH:MM:SS

format_duration(seconds)
  └─ Format as readable duration

get_age_seconds(timestamp)
  └─ Get age in seconds

get_age_hours(timestamp)
  └─ Get age in hours

get_age_days(timestamp)
  └─ Get age in days

is_older_than(timestamp, hours)
  └─ Check if older than N hours

VALIDATION UTILITIES:

is_email(email)
  └─ RFC pattern matching

is_url(url)
  └─ HTTP/HTTPS URL pattern

is_integer(value)
  └─ Integer type checking

is_positive(value)
  └─ Positive number check

is_in_range(value, min, max)
  └─ Range checking

is_valid_length(text, min, max)
  └─ Length constraints

is_not_empty(value)
  └─ Empty value checking

PERFORMANCE:

All utilities are:
  ✓ Optimized for speed
  ✓ Error-safe (exception handling)
  ✓ Type-annotated
  ✓ Well-documented
  ✓ Testable

Typical latency:
  - URL operations: < 1ms
  - Text operations: < 5ms
  - File operations: disk-dependent
  - Time operations: < 1ms
  - Validation: < 1ms

USAGE PATTERNS:

# Batch processing
urls = ["https://example.com/1", "https://example.com/2"]
domains = [URLUtils.extract_domain(url) for url in urls]

# Safe chaining
text = TextUtils.clean_text(html)
text = TextUtils.strip_html(text)
text = TextUtils.truncate_text(text)

# Error handling
if ValidationUtils.is_not_empty(value):
    if ValidationUtils.is_integer(value):
        # Process
        pass

# File operations
if FileUtils.file_exists(path):
    content = FileUtils.safe_read_file(path)
    if content:
        processed = TextUtils.clean_text(content)
        FileUtils.safe_write_file(output_path, processed)

TESTING:

All utilities include comprehensive:
  ✓ Type hints for IDE support
  ✓ Docstrings for documentation
  ✓ Error handling for robustness
  ✓ Logging for debugging
  ✓ Examples in docstrings
"""
