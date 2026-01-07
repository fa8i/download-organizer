"""Utility functions for the Download Organizer."""

import os
from pathlib import Path
from typing import Optional

def get_filesize_human(size_bytes: int) -> str:
    """Convert bytes to a human-readable string (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def extract_path_from_response(text: str) -> Optional[str]:
    """
    Extracts a file path from an agent response using known triggers.
    Supports: 'Archivo guardado en', 'Guardado en', 'Movido a'.
    """
    triggers = ["Archivo guardado en ", "Guardado en ", "Movido a "]
    
    for trigger in triggers:
        if trigger in text:
            path_str = text.split(trigger, 1)[1].strip().rstrip('.')
            # Handle potential surrounding quotes or extra chars if necessary
            # For now, simplistic stripping is usually enough given the agent's instructions
            
            p = Path(path_str)
            if p.exists():
                if p.is_dir():
                    return str(p)
                return str(p.parent)
            
            # Additional check: sometimes agent might output a path that doesn't exist yet 
            # or is relative, but we only return valid existing paths for opening.
            
    return None
