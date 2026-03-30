"""Configuration for the Download Organizer."""

from pathlib import Path
from typing import Dict, List
import subprocess
import os

# =============================================================================
# PATHS
# =============================================================================

def get_downloads_dir() -> Path:
    """Attempts to find the user's Downloads directory across different languages."""
    # 1. Try xdg-user-dir (standard on most Linux distros)
    try:
        result = subprocess.run(['xdg-user-dir', 'DOWNLOAD'], capture_output=True, text=True, check=True)
        path = Path(result.stdout.strip())
        if path.exists():
            return path
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # 2. Try common environment variables
    xdg_downloads = os.environ.get("XDG_DOWNLOAD_DIR")
    if xdg_downloads and Path(xdg_downloads).exists():
        return Path(xdg_downloads)

    # 3. Fallback to common names
    home = Path.home()
    for name in ["Downloads", "Descargas", "Téléchargements"]:
        path = home / name
        if path.exists():
            return path
            
    # Final fallback
    return home / "Downloads"

HOME = Path.home()
DOWNLOADS_DIR = get_downloads_dir()
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

# Icon for notifications (can be a path or a system icon name)
APP_ICON = "folder-download" 

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

LLM_PROVIDER = os.environ.get("LLM_PROVIDER")
LLM_MODEL = os.environ.get("LLM_MODEL")

if not LLM_PROVIDER or not LLM_MODEL:
    # We don't raise an error here to allow other tools (like configure_ui) 
    # to run without LLM env vars, but the agent won't work without them.
    pass
