"""Dialog notifier that spawns the GTK process."""

import subprocess
import sys
import os
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple

from .config import DATA_DIR, DIALOG_TIMEOUT

class DialogResult(Enum):
    CONFIRMED = auto()
    CANCELLED = auto()
    TIMEOUT = auto()

@dataclass
class DialogResponse:
    result: DialogResult
    user_input: Optional[str] = None
    
    @property
    def should_auto_classify(self) -> bool:
        return self.result == DialogResult.TIMEOUT or \
               (self.result == DialogResult.CONFIRMED and not self.user_input)

def _get_filesize_human(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def show_download_dialog(filename: str, file_size: int, timeout: int = DIALOG_TIMEOUT) -> DialogResponse:
    size_human = _get_filesize_human(file_size)
    
    # Run UI as module: python -m download_organizer.ui.window
    cmd = [
        sys.executable, 
        "-m", "download_organizer.ui.window",
        filename, size_human, str(timeout)
    ]
    
    try:
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        # IMPORTANT: Add the package root to PYTHONPATH so the subprocess can find 'download_organizer'
        # sys.path[0] usually contains the script dir, but we want the package root.
        # process.cwd is likely the project root due to systemd WorkingDirectory, but to be safe:
        
        # We know main.py puts parrent of download_organizer in sys.path. 
        # Let's add all sys.path to PYTHONPATH for the child.
        env["PYTHONPATH"] = os.pathsep.join(sys.path)
        
        # DEBUG LOGGING
        print(f"DEBUG: Executing UI command: {cmd}")
        print(f"DEBUG: PYTHONPATH: {env.get('PYTHONPATH')}")
        print(f"DEBUG: DISPLAY: {env.get('DISPLAY')}")
        print(f"DEBUG: XAUTHORITY: {env.get('XAUTHORITY')}")
        print(f"DEBUG: DBUS_SESSION_BUS_ADDRESS: {env.get('DBUS_SESSION_BUS_ADDRESS')}")

        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 5,
            env=env
        )
        
        output = process.stdout.strip()
        stderr = process.stderr.strip()
        print(f"DEBUG: UI process return code: {process.returncode}")
        if output: print(f"DEBUG: ui.py output: {output}")
        if stderr: print(f"DEBUG: ui.py stderr: {stderr}")

        result_str = "timeout"
        user_input = None
        
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith("RESULT:"):
                result_str = line.split(":", 1)[1]
            elif line.startswith("INPUT:"):
                user_input = line.split(":", 1)[1]
        
        if result_str == "confirmed":
            return DialogResponse(DialogResult.CONFIRMED, user_input)
        elif result_str == "cancelled":
            return DialogResponse(DialogResult.CANCELLED)
        else:
            return DialogResponse(DialogResult.TIMEOUT)
            
    except subprocess.TimeoutExpired:
        print("DEBUG: ui.py timed out subprocess")
        return DialogResponse(DialogResult.TIMEOUT)
    except Exception as e:
        print(f"Error showing dialog: {e}")
        # Could fallback to zenity here, but skipping for brevity as UI should work
        return DialogResponse(DialogResult.TIMEOUT)
