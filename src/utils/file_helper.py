"""File helpers for multimodal diagnostic inputs."""

import os
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Supported extensions
TEXT_CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".c", ".cpp", ".h", ".hpp", ".cs",
    ".java", ".kt", ".rs", ".go", ".rb", ".php", ".html", ".css", ".scss",
    ".json", ".yaml", ".yml", ".xml", ".toml", ".ini", ".cfg", ".conf",
    ".sql", ".sh", ".bash", ".ps1", ".bat", ".cmd", ".dockerfile", ".env",
    ".log", ".txt", ".md", ".csv",
    # Hardware / EDA netlists & schematics
    ".sch", ".kicad_pcb", ".kicad_sch", ".net", ".spice", ".cir", ".v", ".sv", ".vhd", ".vhdl"
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".avi", ".mkv", ".m4v"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".aac", ".m4a", ".flac", ".wma"}

def get_file_category(path: str) -> str:
    """Classify file as text, image, video, audio, or unknown."""
    if not path or not os.path.exists(path):
        return "none"
    ext = Path(path).suffix.lower()
    if ext in TEXT_CODE_EXTENSIONS:
        return "text"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in VIDEO_EXTENSIONS:
        return "video"
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    
    # Fallback mime detection
    mime, _ = mimetypes.guess_type(path)
    if mime:
        if mime.startswith("text/"):
            return "text"
        if mime.startswith("image/"):
            return "image"
        if mime.startswith("video/"):
            return "video"
        if mime.startswith("audio/"):
            return "audio"
    return "binary"

def get_file_mime(path: str) -> str:
    """Determine MIME type for a file."""
    mime, _ = mimetypes.guess_type(path)
    if mime:
        return mime
    ext = Path(path).suffix.lower()
    ext_mime_map = {
        ".py": "text/x-python",
        ".js": "text/javascript",
        ".ts": "text/typescript",
        ".cpp": "text/x-c++src",
        ".c": "text/x-csrc",
        ".json": "application/json",
        ".yaml": "text/yaml",
        ".yml": "text/yaml",
        ".sch": "text/plain",
        ".net": "text/plain",
        ".spice": "text/plain",
        ".v": "text/plain",
        ".log": "text/plain",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mov": "video/quicktime",
    }
    return ext_mime_map.get(ext, "application/octet-stream")

def format_file_size(size_bytes: int) -> str:
    """Format bytes into readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def get_file_metadata(path: str) -> Dict[str, Any]:
    """Get metadata for a file."""
    if not path or not os.path.exists(path):
        return {"exists": False}
    p = Path(path)
    size = os.path.getsize(path)
    cat = get_file_category(path)
    mime = get_file_mime(path)
    return {
        "exists": True,
        "name": p.name,
        "path": str(p.resolve()),
        "size": size,
        "size_formatted": format_file_size(size),
        "extension": p.suffix.lower(),
        "category": cat,
        "mime": mime
    }

def read_text_file(path: str, max_lines: int = 1500) -> Tuple[str, bool]:
    """Read text file safely with encoding fallbacks and smart truncation for huge logs."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
    content = ""
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                lines = f.readlines()
                total_lines = len(lines)
                if total_lines > max_lines:
                    # Keep first 400 lines and last 1000 lines (where crash or error trace typically resides)
                    head = lines[:400]
                    tail = lines[-1000:]
                    content = "".join(head) + f"\n\n--- [TRUNCATED {total_lines - 1400} LINES FOR CONTEXT OPTIMIZATION] ---\n\n" + "".join(tail)
                    return content, True
                return "".join(lines), False
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return f"Error reading file: {e}", False
    return "Error: Unable to decode file with standard text encodings.", False
