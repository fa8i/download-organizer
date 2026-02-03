"""Archive extraction tools for the Download Organizer agent."""

import shutil
import subprocess
import zipfile
import tarfile
from pathlib import Path
from typing import Optional

# Supported archive extensions
EXTRACTABLE_EXTENSIONS = {
    ".zip": "zip",
    ".tar": "tar",
    ".tar.gz": "tar",
    ".tgz": "tar", 
    ".tar.bz2": "tar",
    ".tar.xz": "tar",
    ".gz": "gzip",
    ".bz2": "bzip2",
    ".xz": "xz",
    ".rar": "rar",
    ".7z": "7z",
}

from agentify.core.tool import tool

def _can_extract(file_path: str) -> dict:
    """Internal helper to check if a file can be extracted."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if path.name.endswith('.tar.gz'): suffix = '.tar.gz'
    elif path.name.endswith('.tar.bz2'): suffix = '.tar.bz2'
    elif path.name.endswith('.tar.xz'): suffix = '.tar.xz'
    
    if suffix in EXTRACTABLE_EXTENSIONS:
        archive_type = EXTRACTABLE_EXTENSIONS[suffix]
        
        if archive_type == "rar":
            has_tool = shutil.which("unrar") is not None
            if not has_tool:
                return {"extractable": False, "reason": "unrar not installed"}
        elif archive_type == "7z":
            has_tool = shutil.which("7z") is not None
        
        # Fixing logic error in original code: if 7z not installed, it should return False
        if archive_type == "7z" and not has_tool:
             return {"extractable": False, "reason": "7z not installed"}
        
        return {
            "extractable": True,
            "archive_type": archive_type,
            "extension": suffix
        }
    
    return {"extractable": False, "reason": f"Unknown archive format: {suffix}"}

@tool
def can_extract(file_path: str) -> dict:
    """Check if a file can be extracted and what type it is."""
    return _can_extract(file_path)

@tool
def extract_archive(archive_path: str, destination_dir: str, delete_original: bool = False) -> dict:
    """Extract an archive file to a destination directory."""
    try:
        archive = Path(archive_path)
        dest = Path(destination_dir)
        
        if not archive.exists():
            return {"success": False, "message": f"Archive not found: {archive_path}"}
        
        # Use internal helper to avoid @tool wrapper string return
        check = _can_extract(archive_path)
        if not check.get("extractable"):
            return {"success": False, "message": check.get("reason", "Cannot extract")}
        
        archive_type = check["archive_type"]
        dest.mkdir(parents=True, exist_ok=True)
        
        extracted_files = []
        
        if archive_type == "zip":
            with zipfile.ZipFile(archive, 'r') as zf:
                zf.extractall(dest)
                extracted_files = zf.namelist()
        elif archive_type == "tar":
            with tarfile.open(archive, 'r:*') as tf:
                tf.extractall(dest)
                extracted_files = tf.getnames()
        elif archive_type == "gzip":
            import gzip
            output_path = dest / archive.stem
            with gzip.open(archive, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            extracted_files = [str(output_path)]
        elif archive_type == "rar":
            result = subprocess.run(["unrar", "x", "-o+", str(archive), str(dest) + "/"], capture_output=True, text=True)
            if result.returncode != 0:
                return {"success": False, "message": f"RAR extraction failed: {result.stderr}"}
            extracted_files = ["(RAR contents)"]
        elif archive_type == "7z":
            result = subprocess.run(["7z", "x", f"-o{dest}", "-y", str(archive)], capture_output=True, text=True)
            if result.returncode != 0:
                return {"success": False, "message": f"7z extraction failed: {result.stderr}"}
            extracted_files = ["(7z contents)"]
        else:
            return {"success": False, "message": f"Unsupported archive type: {archive_type}"}
        
        if delete_original:
            archive.unlink()
        
        return {
            "success": True, 
            "message": f"Extracted to {dest}", 
            "extracted_to": str(dest), 
            "files_count": len(extracted_files)
        }
        
    except Exception as e:
        return {"success": False, "message": f"Extraction error: {str(e)}"}
