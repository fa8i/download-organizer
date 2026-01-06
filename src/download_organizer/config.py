"""Configuration for the Download Organizer."""

from pathlib import Path
from typing import Dict, List

# =============================================================================
# PATHS
# =============================================================================

HOME = Path.home()
DOWNLOADS_DIR = HOME / "Descargas"
DATA_DIR = HOME / ".local" / "share" / "download-organizer"
DB_PATH = DATA_DIR / "history.db"

# =============================================================================
# FILE CATEGORIES (for auto-classification)
# =============================================================================

CATEGORIES: Dict[str, List[str]] = {
    "Imágenes": [
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", 
        ".bmp", ".ico", ".heic", ".tiff", ".raw"
    ],
    "Documentos": [
        ".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf",
        ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".md"
    ],
    "Videos": [
        ".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", 
        ".wmv", ".m4v", ".mpeg"
    ],
    "Música": [
        ".mp3", ".flac", ".wav", ".ogg", ".m4a", ".aac", 
        ".wma", ".opus"
    ],
    "Comprimidos": [
        ".zip", ".rar", ".tar", ".gz", ".7z", ".bz2", 
        ".xz", ".tar.gz", ".tgz"
    ],
    "Código": [
        ".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", 
        ".go", ".rs", ".html", ".css", ".json", ".yaml", ".yml"
    ],
}

# =============================================================================
# DIALOG SETTINGS
# =============================================================================

DIALOG_TIMEOUT = 45  # seconds before auto-classify

# Patterns to ignore (incomplete downloads)
IGNORED_PATTERNS = [
    ".part",        # Firefox partial
    ".crdownload",  # Chrome partial  
    ".tmp",
    ".temp",
    ".download",
    "~",            # Backup files
]

# =============================================================================
# LLM CONFIGURATION
# =============================================================================

LLM_PROVIDER = "openai"
LLM_MODEL = "gpt-4.1"
