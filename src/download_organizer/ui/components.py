import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Pango

class DownloadCard(Gtk.Box):
    """Reusable widget displaying the download info and action controls."""
    def __init__(self, filename="example.zip", size_human="15 MB", 
                 on_confirm=None, on_cancel=None, time_left=30, content_config=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add_css_class("main-window")
        
        self.on_confirm_callback = on_confirm
        self.on_cancel_callback = on_cancel
        self.time_left = time_left
        
        # Default content if none provided
        self.content = content_config or {
            "title_text": "Nueva descarga",
            "placeholder_text": "Instrucción (Enter para auto)...",
            "btn_confirm": "Organizar",
            "btn_cancel": "Cancelar"
        }
        
        self._setup_ui(filename, size_human)

    def _setup_ui(self, filename, size_human):
        # Title
        title = Gtk.Label(label=self.content.get("title_text", "Nueva descarga"))
        title.set_xalign(0)
        title.add_css_class("title")
        self.append(title)
        
        # Filename
        file_label = Gtk.Label(label=f"{filename}  ({size_human})")
        file_label.set_xalign(0)
        file_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        file_label.add_css_class("filename")
        self.append(file_label)
        
        self.append(Gtk.Box(height_request=12))
        
        # Entry
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text(self.content.get("placeholder_text", "..."))
        if self.on_confirm_callback:
            self.entry.connect("activate", lambda w: self.on_confirm_callback(self.entry.get_text()))
        self.append(self.entry)
        
        # Actions Row
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        self.timer_label = Gtk.Label(label=f"{self.time_left}s")
        self.timer_label.add_css_class("timer")
        self.timer_label.set_halign(Gtk.Align.START)
        action_box.append(self.timer_label)
        
        spacer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        spacer.set_hexpand(True)
        action_box.append(spacer)
        
        self.cancel_btn = Gtk.Button(label=self.content.get("btn_cancel", "Cancelar"))
        self.cancel_btn.add_css_class("cancel-action")
        # We don't disable it by default here to make preview more useful, 
        # or we let the controller handle sensitivity.
        self.cancel_btn.set_sensitive(True) 
        if self.on_cancel_callback:
             self.cancel_btn.connect("clicked", lambda w: self.on_cancel_callback())
        action_box.append(self.cancel_btn)
        
        confirm_btn = Gtk.Button(label=self.content.get("btn_confirm", "Organizar"))
        confirm_btn.add_css_class("suggested-action")
        if self.on_confirm_callback:
            confirm_btn.connect("clicked", lambda w: self.on_confirm_callback(self.entry.get_text()))
        action_box.append(confirm_btn)
        
        self.append(action_box)

    def update_timer(self, seconds):
        """Updates the timer label text."""
        self.time_left = seconds
        self.timer_label.set_label(f"{seconds}s")
