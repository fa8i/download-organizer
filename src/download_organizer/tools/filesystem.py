"""Filesystem tools for the Download Organizer Agent."""

import shutil
import os
from pathlib import Path

from agentify.core.tool import tool

@tool
def move_file(source_path: str, destination_dir: str) -> dict:
    """
    Moves a file to a destination directory.
    
    Args:
        source_path: Absolute path to the source file.
        destination_dir: Absolute path to the destination directory.
    """
    try:
        src = Path(source_path)
        dst_dir = Path(destination_dir)
        
        if not src.exists():
            return {"success": False, "message": f"Source file not found: {source_path}"}
            
        if not dst_dir.exists():
            # Auto-create destination if it doesn't exist (agent convenience)
            dst_dir.mkdir(parents=True, exist_ok=True)
            
        dst_path = dst_dir / src.name
        if dst_path.exists():
            stem = src.stem
            suffix = src.suffix
            counter = 1
            while dst_path.exists():
                dst_path = dst_dir / f"{stem} ({counter}){suffix}"
                counter += 1
                
        shutil.move(str(src), str(dst_path))
        return {"success": True, "message": f"Moved to {dst_path}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@tool
def rename_file(file_path: str, new_name: str) -> dict:
    """
    Renames a file in place.
    
    Args:
        file_path: Absolute path to the file.
        new_name: New filename (with extension).
    """
    try:
        src = Path(file_path)
        if not src.exists():
            return {"success": False, "message": f"File not found: {file_path}"}
            
        dst = src.parent / new_name
        if dst.exists():
             path_dst = Path(dst)
             stem = path_dst.stem
             suffix = path_dst.suffix
             counter = 1
             while dst.exists():
                 dst = src.parent / f"{stem} ({counter}){suffix}"
                 counter += 1
            
        src.rename(dst)
        return {"success": True, "message": f"Renamed to {dst}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@tool
def create_directory(path: str) -> dict:
    """Creates a directory."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return {"success": True, "message": f"Created {path}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@tool
def list_home_directories(root_path: str = None) -> dict:
    """Lists directories in home or specified path."""
    try:
        if root_path is None:
            root_path = Path.home()
        else:
            root_path = Path(root_path)
            
        if not root_path.exists():
            return {"success": False, "message": "Path not found"}
            
        dirs = [d.name for d in root_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        return {"success": True, "directories": dirs}
    except Exception as e:
        return {"success": False, "message": str(e)}

@tool
def get_file_info(file_path: str) -> dict:
    """Gets metadata about a file."""
    try:
        p = Path(file_path)
        if not p.exists():
            return {"success": False, "message": "File not found"}
            
        stats = p.stat()
        return {
            "success": True,
            "name": p.name,
            "suffix": p.suffix,
            "size_bytes": stats.st_size,
            "stem": p.stem,
            "parent": str(p.parent)
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

@tool
def delete_file(file_path: str) -> dict:
    """
    Deletes a file permanently.
    
    Args:
        file_path: Absolute path to the file to delete.
    """
    try:
        p = Path(file_path)
        if not p.exists():
            return {"success": False, "message": f"File not found: {file_path}"}
            
        if p.is_dir():
             return {"success": False, "message": f"Path is a directory, not a file: {file_path}"}
             
        p.unlink()
        return {"success": True, "message": f"Deleted {file_path}"}
    except Exception as e:
        return {"success": False, "message": str(e)}
