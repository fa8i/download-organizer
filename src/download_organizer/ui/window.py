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
        print("Error: PyGObject (gi) not found. Please install: sudo apt install python3-gi")
        sys.exit(1)

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib, Pango

# Relative import for config
from ..config import DIALOG_TIMEOUT

CSS = """
/* Modern Deep Purple Theme */
window {
    background-color: transparent;
}
.main-window {
    background-color: #171421;
    color: #e0d0f5;
    border-radius: 12px;
    border: 1px solid #2e213b;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
    padding: 20px;
}
label { color: #e0d0f5; }
.title { font-size: 16px; font-weight: 700; color: #cba6f7; margin-bottom: 4px; }
.filename { font-size: 13px; font-weight: 600; color: #ffffff; margin-bottom: 2px; }
.subtitle { font-size: 11px; color: #7a6f8b; margin-bottom: 15px; }
entry {
    background-color: #1a1223; color: #ffffff; border: 1px solid #2e213b;
    border-radius: 6px; padding: 8px 12px; margin-bottom: 15px;
    caret-color: #a87ffb; transition: all 200ms ease; font-size: 13px;
}
entry:focus { border-color: #a87ffb; background-color: #241930; }
button {
    background-color: #1a1223; color: #e0d0f5; border: 1px solid #2e213b;
    border-radius: 6px; padding: 6px 14px; font-size: 12px; font-weight: 600;
    transition: all 200ms ease; min-height: 28px;
}
button:hover { background-color: #2e213b; border-color: #4a3b5c; color: #ffffff; }
button.suggested-action { background-color: #6233a3; color: #ffffff; border-color: #6233a3; }
button.suggested-action:hover { background-color: #7b42cc; border-color: #7b42cc; box-shadow: 0 2px 8px rgba(98, 51, 163, 0.4); }
.timer { font-size: 11px; color: #554b66; margin-top: 4px; }
"""

class DownloadDialog(Gtk.ApplicationWindow):
    def __init__(self, app, filename, size_human, timeout_sec):
        super().__init__(application=app)
        self.app = app
        self.filename = filename
        self.user_input = None
        self.is_timeout = False
        self.is_cancelled = False
        
        self.set_title("Download Organizer")
        self.set_default_size(400, 160)
        self.set_resizable(False)
        self.set_decorated(False)
        
        self.timeout_id = GLib.timeout_add(timeout_sec * 1000, self.on_timeout)
        self.timer_label = None
        self.time_left = timeout_sec
        GLib.timeout_add(1000, self.update_timer)

        self._setup_ui(filename, size_human)
        self._load_css()
        
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)
        
        self.start_time = time.time()

    def _setup_ui(self, filename, size_human):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.add_css_class("main-window")
        self.set_child(main_box)
        
        title = Gtk.Label(label="Nueva descarga")
        title.set_xalign(0)
        title.add_css_class("title")
        main_box.append(title)
        
        file_label = Gtk.Label(label=f"{filename}  ({size_human})")
        file_label.set_xalign(0)
        file_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        file_label.add_css_class("filename")
        main_box.append(file_label)
        
        main_box.append(Gtk.Box(height_request=12))
        
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Instrucción (Enter para auto)...")
        self.entry.connect("activate", self.on_confirm)
        main_box.append(self.entry)
        self.entry.grab_focus()
        
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        self.timer_label = Gtk.Label(label=f"{self.time_left}s")
        self.timer_label.add_css_class("timer")
        self.timer_label.set_halign(Gtk.Align.START)
        action_box.append(self.timer_label)
        
        spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        spacer.set_hexpand(True)
        action_box.append(spacer)
        
        self.cancel_btn = Gtk.Button(label="Cancelar")
        self.cancel_btn.set_sensitive(False)  # Safety delay
        self.cancel_btn.connect("clicked", self.on_cancel)
        action_box.append(self.cancel_btn)
        
        confirm_btn = Gtk.Button(label="Organizar")
        confirm_btn.add_css_class("suggested-action")
        confirm_btn.connect("clicked", self.on_confirm)
        action_box.append(confirm_btn)
        
        main_box.append(action_box)

    def _load_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def update_timer(self):
        if getattr(self, 'cancel_btn', None) and not self.cancel_btn.get_sensitive():
            # Wait 0.3s before enabling cancel
            if time.time() - self.start_time > 0.3:
                self.cancel_btn.set_sensitive(True)

        self.time_left -= 1
        if self.timer_label:
            self.timer_label.set_label(f"{self.time_left}s")
        return self.time_left > 0 and not self.is_timeout

    def on_timeout(self):
        self.is_timeout = True
        self.app.quit()
        return False

    def on_confirm(self, widget):
        self.user_input = self.entry.get_text()
        self.app.quit()

    def on_cancel(self, widget):
        print(f"DEBUG: on_cancel triggered by {widget}")
        self.is_cancelled = True
        self.app.quit()
        
    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            if time.time() - self.start_time < 0.3:
                print("DEBUG: Ignored early Escape key")
                return True
            self.on_cancel("EscapeKey")
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
            print(f"Error in dialog: {e}")
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
