import sys
import os
import subprocess
import time

try:
    import gi
except ImportError:
    # Fallback to system packages if not in venv
    sys.path.append("/usr/lib/python3/dist-packages")
    try:
        import gi
    except ImportError:
        print("Error: PyGObject (gi) not found. Please install: sudo apt install python3-gi", file=sys.stderr)
        sys.exit(1)

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib, Pango

# Relative import for config and theme
from ..config import DIALOG_TIMEOUT
from .theme_manager import ThemeManager
from .components import DownloadCard

class DownloadDialog(Gtk.ApplicationWindow):
    def __init__(self, app, filename, size_human, timeout_sec):
        super().__init__(application=app)
        self.app = app
        self.filename = filename
        self.user_input = None
        self.is_timeout = False
        self.is_cancelled = False
        
        # Initialize Theme Manager
        self.theme_manager = ThemeManager()
        
        self.set_title("Download Organizer")
        
        # Geometry from config
        geo = self.theme_manager.config.geometry
        width = geo.get("width", 400)
        height = geo.get("height", 160)
        self.set_default_size(width, height)
        
        self.set_resizable(False)
        self.set_decorated(False)
        
        self.timeout_id = GLib.timeout_add(timeout_sec * 1000, self.on_timeout)
        self.time_left = timeout_sec
        GLib.timeout_add(1000, self.update_timer)

        self._setup_ui(filename, size_human)
        self._load_css()
        
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)
        
        self.start_time = time.time()

    def _setup_ui(self, filename, size_human):
        self.card = DownloadCard(
            filename=filename, 
            size_human=size_human,
            on_confirm=self.on_finalize_confirm,
            on_cancel=self.on_finalize_cancel,
            time_left=self.time_left,
            content_config=self.theme_manager.config.content
        )
        self.set_child(self.card)

    def _load_css(self):
        provider = Gtk.CssProvider()
        css_data = self.theme_manager.generate_css()
        try:
            provider.load_from_data(css_data.encode())
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"Error loading CSS: {e}", file=sys.stderr)

    def update_timer(self):
        # Delegate to card
        if hasattr(self, 'card'):
             # Logic for Cancel button sensitivity
             if not self.card.cancel_btn.get_sensitive():
                if time.time() - self.start_time > 0.3:
                    self.card.cancel_btn.set_sensitive(True)
             
             self.card.update_timer(self.time_left)

        self.time_left -= 1
        return self.time_left > 0 and not self.is_timeout

    def on_timeout(self):
        self.is_timeout = True
        self.app.quit()
        return False

    def on_finalize_confirm(self, text):
        self.user_input = text
        self.app.quit()

    def on_finalize_cancel(self, *args):
        self.is_cancelled = True
        self.app.quit()

        
    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            if time.time() - self.start_time < 0.3:
                print("DEBUG: Ignored early Escape key", file=sys.stderr)
                return True
            self.on_finalize_cancel("EscapeKey")
            return True
        return False

class OrganizerApp(Gtk.Application):
    def __init__(self, filename, size_human, timeout):
        super().__init__(application_id="com.fabian.download_organizer", flags=0)
        self.filename = filename
        self.size_human = size_human
        self.timeout = timeout

    def do_activate(self):
        win = DownloadDialog(self, self.filename, self.size_human, self.timeout)
        win.present()
        self.win = win

    def run_dialog(self):
        try:
            self.run(None)
            if hasattr(self, 'win'):
                if self.win.is_cancelled: return "cancelled", None
                elif self.win.is_timeout: return "timeout", None
                elif self.win.user_input is not None: return "confirmed", self.win.user_input
            return "timeout", None
        except Exception as e:
            print(f"Error in dialog: {e}", file=sys.stderr)
            return "error", None

def show_modern_dialog(filename, size_human, timeout=30):
    app = OrganizerApp(filename, size_human, timeout)
    status, text = app.run_dialog()
    return status, text

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("size")
    parser.add_argument("timeout", type=int)
    args = parser.parse_args()
    
    status, text = show_modern_dialog(args.filename, args.size, args.timeout)
    print(f"RESULT:{status}")
    if text: print(f"INPUT:{text}")
