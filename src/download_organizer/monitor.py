"""Watchdog-based file monitor for the Downloads folder."""

import time
import logging
from pathlib import Path
from typing import Callable, Optional, Set, Dict
from dataclasses import dataclass

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from .config import DOWNLOADS_DIR
from .categorizer import should_ignore_file


@dataclass
class PendingFile:
    """A file pending processing."""
    path: str
    detected_at: float
    size: int = 0
    stable_checks: int = 0


class DownloadEventHandler(FileSystemEventHandler):
    """Handler for new file events in the Downloads folder."""
    
    def __init__(self, callback: Callable[[str], None]):
        super().__init__()
        self.callback = callback
        self._pending: Dict[str, PendingFile] = {}
        self._processed: Set[str] = set()
    
    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory: return
        self._add_to_pending(event.src_path)
    
    def on_modified(self, event) -> None:
        if event.is_directory: return
        if event.src_path in self._pending:
            self._pending[event.src_path].stable_checks = 0

    def on_moved(self, event) -> None:
        if event.is_directory: return
        # Handle rename/move: if old path was processed, mark new path as processed too
        if event.src_path in self._processed:
            self._processed.remove(event.src_path)
            self._processed.add(event.dest_path)
            logging.debug(f"File moved from {event.src_path} to {event.dest_path}, keeping processed state.")
        else:
            self._add_to_pending(event.dest_path)

    def on_deleted(self, event) -> None:
        if event.is_directory: return
        if event.src_path in self._processed:
            self._processed.remove(event.src_path)
            # Also remove from pending if it was there
            self._pending.pop(event.src_path, None)

    def _add_to_pending(self, path: str):
        if should_ignore_file(path): return
        self._pending[path] = PendingFile(path=path, detected_at=time.time())

    def check_pending_files(self) -> list[str]:
        ready_files = []
        to_remove = []
        
        for path, pending in self._pending.items():
            if path in self._processed:
                to_remove.append(path)
                continue
            
            p = Path(path)
            if not p.exists():
                to_remove.append(path)
                continue
            
            try:
                current_size = p.stat().st_size
                if current_size == pending.size:
                    pending.stable_checks += 1
                else:
                    pending.size = current_size
                    pending.stable_checks = 0
                
                # Buffer ~0.3s (3 checks @ 0.1s)
                if pending.stable_checks >= 3:
                    if not should_ignore_file(path):
                        ready_files.append(path)
                        self._processed.add(path)
                    to_remove.append(path)
            except OSError:
                to_remove.append(path)
        
        for p in to_remove:
            self._pending.pop(p, None)
            
        return ready_files


class DownloadMonitor:
    def __init__(self, on_new_file: Callable[[str], None], watch_dir: Optional[Path] = None):
        self.watch_dir = watch_dir or DOWNLOADS_DIR
        self.on_new_file = on_new_file
        self._observer: Optional[Observer] = None
        self._handler: Optional[DownloadEventHandler] = None
        self._running = False
    
    def start(self) -> None:
        if self._running: return
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self._handler = DownloadEventHandler(self.on_new_file)
        self._observer = Observer()
        self._observer.schedule(self._handler, str(self.watch_dir), recursive=False)
        self._observer.start()
        self._running = True
        logging.info(f"Monitoring: {self.watch_dir}")
    
    def stop(self) -> None:
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None
        self._running = False
        logging.info("Monitor stopped")
    
    def check_and_process(self) -> int:
        """Checks for pending files and processes them. Returns number of files pending/processed."""
        if not self._handler: return 0
        
        pending_files = self._handler.check_pending_files()
        count = len(pending_files)
        
        # Also count if we have any pending in the dict, to keep fast loop while stabilizing
        if self._handler._pending:
            count += len(self._handler._pending)
            
        for f in pending_files:
            try:
                self.on_new_file(f)
            except Exception as e:
                logging.error(f"Error processing {f}: {e}")
                
        return count

def run_monitor_loop(on_new_file: Callable[[str], None]) -> None:
    monitor = DownloadMonitor(on_new_file)
    try:
        monitor.start()
        while True:
            # Check for files
            processed_count = monitor.check_and_process()
            
            # Dynamic sleep to save CPU
            if processed_count > 0:
                time.sleep(0.1)
            else:
                time.sleep(1.0)
                
    except KeyboardInterrupt:
        logging.info("\nInterrupted by user")
    finally:
        monitor.stop()
