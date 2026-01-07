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

from .utils import get_filesize_human

def show_download_dialog(filename: str, file_size: int, timeout: int = DIALOG_TIMEOUT) -> DialogResponse:
    size_human = get_filesize_human(file_size)
    
    # Run UI as module: python -m download_organizer.ui.window
    cmd = [
        sys.executable, 
        "-m", "download_organizer.ui.window",
        filename, size_human, str(timeout)
    ]
    
    try:
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONPATH"] = os.pathsep.join(sys.path)
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 5,
            env=env
        )
        
        output = process.stdout.strip()
        
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
        return DialogResponse(DialogResult.TIMEOUT)
    except Exception as e:
        print(f"Error showing dialog: {e}")
        return DialogResponse(DialogResult.TIMEOUT)

def show_system_notification(title: str, message: str, folder_path: str = None):
    """Shows an interactive notification using our ui/notification.py script."""
    cmd = [
        sys.executable,
        "-m", "download_organizer.ui.notification",
        title, message
    ]
    if folder_path:
        cmd.append(folder_path)
    
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(sys.path)
        subprocess.Popen(cmd, env=env) # Use Popen to not block the main process
    except Exception as e:
        print(f"Failed to show notification: {e}")
