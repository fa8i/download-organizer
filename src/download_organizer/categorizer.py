"""Auto-categorizer for files based on extension."""

from pathlib import Path
from typing import Optional, Tuple
from .config import CATEGORIES, DOWNLOADS_DIR, IGNORED_PATTERNS

def get_category_for_extension(extension: str) -> Optional[str]:
    """Get the category name for a file extension."""
    ext = extension.lower()
    if not ext.startswith('.'):
        ext = f'.{ext}'
    
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return None

def get_default_destination(file_path: str) -> Tuple[str, str]:
    """Get the default destination for a file based on its extension."""
    path = Path(file_path)
    extension = path.suffix.lower()
    
    category = get_category_for_extension(extension)
    
    if category:
        destination = DOWNLOADS_DIR / category
    else:
        destination = DOWNLOADS_DIR / "Otros"
    
    return str(destination), category or "Otros"

def should_ignore_file(file_path: str) -> bool:
    """Check if a file should be ignored."""
    path = Path(file_path)
    name = path.name.lower()
    
    # Check ignored patterns
    for pattern in IGNORED_PATTERNS:
        if name.endswith(pattern):
            return True
    
    # Ignore hidden files
    if name.startswith('.'):
        return True
    
    # Removed size check as requested (fixed issue with small files)
    
    return False
