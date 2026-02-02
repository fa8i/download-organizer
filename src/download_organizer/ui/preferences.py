
import sys
import gi
import logging
from copy import deepcopy

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib

from .theme_manager import ThemeManager, DEFAULT_CONFIG
from .components import DownloadCard

logger = logging.getLogger(__name__)

class PreferencesWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.app = app
        self.set_title("Preferences - Download Organizer")
        self.set_default_size(950, 650)
        
        self.theme_manager = ThemeManager()
        # Work on a copy to support Cancel/Preview
        self.original_config = deepcopy(self.theme_manager.config)
        self.config = deepcopy(self.original_config)
        
        # Monkey-patch theme_manager config for preview generation
        self.theme_manager.config = self.config
        
        # Store widget references for syncing
        self.widgets = {}
        
        self._setup_ui()
        self._apply_css()

    def _setup_ui(self):
        # Main Split Structure
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_position(380) # Widen sidebar for more controls
        self.set_child(paned)
        
        # --- LEFT PANEL: Sidebar / Controls ---
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.add_css_class("sidebar")
        
        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header_box.set_margin_top(20)
        header_box.set_margin_bottom(10)
        header_box.set_margin_start(20)
        
        title_lbl = Gtk.Label(label="Personalization", xalign=0)
        title_lbl.add_css_class("sidebar-header")
        header_box.append(title_lbl)
        
        subtitle_lbl = Gtk.Label(label="Customize your download experience", xalign=0)
        subtitle_lbl.add_css_class("subtitle")
        header_box.append(subtitle_lbl)
        
        sidebar_box.append(header_box)
        
        # Navigation Stack Switcher
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        
        switcher = Gtk.StackSwitcher()
        switcher.set_stack(stack)
        switcher.set_halign(Gtk.Align.CENTER)
        switcher.set_margin_bottom(20)
        sidebar_box.append(switcher)
        
        # Pages Container
        controls_scroller = Gtk.ScrolledWindow()
        controls_scroller.set_vexpand(True)
        controls_scroller.set_child(stack)
        sidebar_box.append(controls_scroller)
        
        # PAGE 1: GENERAL (Presets + Geometry)
        stack.add_titled(self._build_general_page(), "general", "General")
        
        # PAGE 2: COLORS (Granular)
        stack.add_titled(self._build_colors_page(), "colors", "Colors")
        
        # PAGE 3: CONTENT (Text)
        stack.add_titled(self._build_content_page(), "content", "Text & Labels")

        # FOOTER ACTIONS
        actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        actions_box.set_margin_top(10)
        actions_box.set_margin_bottom(20)
        actions_box.set_margin_start(20)
        actions_box.set_margin_end(20)
        
        btn_revert = Gtk.Button(label="Reset")
        btn_revert.add_css_class("destructive-action")
        btn_revert.connect("clicked", self._on_revert)
        actions_box.append(btn_revert)
        
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        actions_box.append(spacer)
        
        btn_cancel = Gtk.Button(label="Cancel")
        btn_cancel.connect("clicked", lambda w: self.app.quit())
        actions_box.append(btn_cancel)

        btn_done = Gtk.Button(label="Save & Close")
        btn_done.add_css_class("suggested-action")
        btn_done.connect("clicked", self._on_done)
        actions_box.append(btn_done)
        
        sidebar_box.append(actions_box)
        
        # Lock sidebar
        paned.set_start_child(sidebar_box)
        paned.set_resize_start_child(False)
        paned.set_shrink_start_child(False)
        
        # --- RIGHT PANEL: Preview ---
        preview_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        preview_frame.add_css_class("preview-pane")
        
        # Centering box for the card
        center_box = Gtk.CenterBox()
        center_box.set_margin_top(60)
        self.preview_card = DownloadCard(
            filename="invoice_2024.pdf", 
            size_human="2.4 MB",
            time_left=45,
            content_config=self.config.content # Pass working copy
        )
        self.preview_card.set_valign(Gtk.Align.CENTER)
        self.preview_card.set_halign(Gtk.Align.CENTER)
        
        center_box.set_center_widget(self.preview_card)
        self._update_preview_geometry()
        preview_frame.append(center_box)
        
        paned.set_end_child(preview_frame)
        paned.set_resize_end_child(True)
        paned.set_shrink_end_child(True)

    def _build_page_box(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(10)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        return box

    def _build_general_page(self):
        page = self._build_page_box()
        
        page.append(self._build_section_header("Quick Presets"))
        presets_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        presets_box.set_homogeneous(True)
        
        for name, label in [("dark", "Dark"), ("light", "Light")]:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", lambda w, n=name: self._apply_preset(n))
            presets_box.append(btn)
        page.append(presets_box)
        
        page.append(self._build_section_header("Window Dimensions"))
        
        page.append(self._build_spin_row("Width (px)", "geometry", "width", 300, 800, 10))
        page.append(self._build_spin_row("Height (px)", "geometry", "height", 100, 600, 10))
        page.append(self._build_spin_row("Corner Radius (px)", "appearance", "border_radius", 0, 32, 1))
        page.append(self._build_spin_row("Font Scale (em)", "appearance", "font_size_scale", 0.8, 2.0, 0.1))

        return page

    def _build_colors_page(self):
        page = self._build_page_box()
        
        page.append(self._build_section_header("Base Colors"))
        page.append(self._build_color_row("Background (Window)", "bg_color"))
        page.append(self._build_color_row("Border", "border_color"))
        
        page.append(self._build_section_header("Text Colors"))
        page.append(self._build_color_row("Title Color", "title_color"))
        page.append(self._build_color_row("Filename Color", "file_color"))
        
        page.append(self._build_section_header("Input Field"))
        page.append(self._build_color_row("Background", "entry_bg"))
        page.append(self._build_color_row("Text Color", "entry_text_color"))
        
        page.append(self._build_section_header("Primary Buttons"))
        page.append(self._build_color_row("Background", "button_bg"))
        page.append(self._build_color_row("Text Color", "button_text_color"))
        
        page.append(self._build_section_header("Cancel Button"))
        page.append(self._build_color_row("Background", "cancel_bg"))
        page.append(self._build_color_row("Text Color", "cancel_fg"))

        page.append(self._build_section_header("Accent"))
        page.append(self._build_color_row("Accent Color", "accent_color"))
        page.append(self._build_color_row("Accent Hover", "accent_hover"))
        
        return page

    def _build_content_page(self):
        page = self._build_page_box()
        
        page.append(self._build_section_header("Interface Text"))
        
        page.append(self._build_text_row("Title", "title_text"))
        page.append(self._build_text_row("Placeholder", "placeholder_text"))
        page.append(self._build_text_row("Confirm Button", "btn_confirm"))
        page.append(self._build_text_row("Cancel Button", "btn_cancel"))
        
        return page

    # --- WIDGET BUILDERS ---

    def _build_section_header(self, text):
        lbl = Gtk.Label(label=text, xalign=0)
        lbl.add_css_class("section-header")
        return lbl

    def _build_color_row(self, label_text, config_key):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl = Gtk.Label(label=label_text, xalign=0)
        lbl.set_hexpand(True)
        row.append(lbl)
        
        rgba = Gdk.RGBA()
        fallback = "#ffffff"
        val = self.config.appearance.get(config_key, fallback)
        try:
             rgba.parse(val)
        except:
             rgba.parse(fallback)
        
        btn = Gtk.ColorButton()
        btn.props.rgba = rgba
        # Force size
        btn.set_valign(Gtk.Align.CENTER)
        btn.connect("color-set", lambda b: self._on_color_change(b, config_key))
        row.append(btn)
        
        # Register for sync
        self.widgets[f"appearance.{config_key}"] = btn
        
        return row

    def _build_spin_row(self, label_text, section, key, lower, upper, step):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl = Gtk.Label(label=label_text, xalign=0)
        lbl.set_hexpand(True)
        row.append(lbl)
        
        current_val = float(getattr(self.config, section).get(key, lower))
        adj = Gtk.Adjustment(value=current_val, lower=lower, upper=upper, step_increment=step, page_increment=step*2)
        spin = Gtk.SpinButton(adjustment=adj, climb_rate=step, digits=1 if isinstance(step, float) else 0)
        spin.connect("value-changed", lambda s: self._on_spin_change(s, section, key))
        row.append(spin)
        
        # Register for sync
        self.widgets[f"{section}.{key}"] = spin
        
        return row

    def _build_text_row(self, label_text, key):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        lbl = Gtk.Label(label=label_text, xalign=0)
        lbl.add_css_class("control-label")
        box.append(lbl)
        
        entry = Gtk.Entry()
        entry.set_text(self.config.content.get(key, ""))
        entry.connect("changed", lambda e: self._on_text_change(e, key))
        box.append(entry)
        
        # Register for sync
        self.widgets[f"content.{key}"] = entry
        
        return box

    # --- HANDLERS ---

    def _on_spin_change(self, spin, section, key):
        val = spin.get_value()
        # Convert to int if it was originally int-like in logic (simplified check)
        if key in ["width", "height", "border_radius"]:
            val = int(val)
        getattr(self.config, section)[key] = val
        
        # If geometry changed, resize preview
        if section == "geometry":
             self._update_preview_geometry()
             
        self._apply_css()

    def _on_color_change(self, btn, key):
        rgba = btn.props.rgba
        color_str = f"#{int(rgba.red*255):02x}{int(rgba.green*255):02x}{int(rgba.blue*255):02x}"
        self.config.appearance[key] = color_str
        self._apply_css()

    def _on_text_change(self, entry, key):
        self.config.content[key] = entry.get_text()
        self._recreate_preview()

    def _on_revert(self, btn):
        """Reverts configuration to the state when the window was opened."""
        self.config = deepcopy(self.original_config)
        
        # Update UI controls to match the reverted config
        self._update_ui_from_config()
        
        # Update Preview
        self.theme_manager.config = self.config
        self._apply_css()
        self._recreate_preview()
        print("Reverted to session start.")

    def _update_ui_from_config(self):
        """Synchronizes all UI widgets with current self.config values."""
        for key, widget in self.widgets.items():
            section, name = key.split(".", 1)
            
            # Get value from config
            if section == "appearance":
                val = self.config.appearance.get(name)
            elif section == "geometry":
                val = self.config.geometry.get(name)
            elif section == "content":
                val = self.config.content.get(name)
            else:
                continue
                
            # Update Widget
            if isinstance(widget, Gtk.ColorButton):
                rgba = Gdk.RGBA()
                try:
                    rgba.parse(val or "#000000")
                    widget.props.rgba = rgba
                except: pass
            elif isinstance(widget, Gtk.SpinButton):
                widget.set_value(float(val))
            elif isinstance(widget, Gtk.Entry):
                widget.set_text(str(val))

    def _on_done(self, btn):
        self.theme_manager.save_config(self.config)
        self.app.quit()

    def _apply_preset(self, preset_name):
        if preset_name == "dark":
             self.config.appearance.update(DEFAULT_CONFIG["appearance"])
        elif preset_name == "light":
             self.config.appearance.update({
                 "bg_color": "#deddda",
                 "title_color": "#6233a3",
                 "file_color": "#1a1a1a",
                 "subtext_color": "#666666",
                 "entry_bg": "#e2e2e2",
                 "entry_text_color": "#000000",
                 "button_bg": "#f0f0f0",
                 "button_text_color": "#ffffff",
                 "cancel_bg": "#e0e0e0",
                 "cancel_fg": "#ffffff",
                 "accent_color": "#6233a3",
                 "border_color": "#c0bfbc",
                 "border_radius": 15
             })
        self._apply_css()
        self._update_ui_from_config() # Sync UI with preset values
        print("Preset applied. Values updated.")

    # --- LOGIC ---

    def _apply_css(self):
        css_data = self.theme_manager.generate_css()
        
        # Preferences Window Styling
        css_data += """
        .sidebar { background-color: #242424; color: #ffffff; }
        .sidebar-header { font-size: 20px; font-weight: 800; font-family: "Sans"; }
        .subtitle { font-size: 13px; color: #aaaaaa; margin-bottom: 10px; }
        .section-header { font-size: 11px; font-weight: bold; text-transform: uppercase; color: #888; margin-top: 15px; margin-bottom: 5px; }
        .control-label { font-size: 13px; color: #dddddd; }
        .preview-pane { 
            background-color: #333333; 
            background-image: linear-gradient(45deg, #2a2a2a 25%, transparent 25%), 
                              linear-gradient(-45deg, #2a2a2a 25%, transparent 25%), 
                              linear-gradient(45deg, transparent 75%, #2a2a2a 75%), 
                              linear-gradient(-45deg, transparent 75%, #2a2a2a 75%);
            background-size: 20px 20px;
            background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
        }
        """
        
        provider = Gtk.CssProvider()
        try:
            provider.load_from_data(css_data.encode())
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"Error loading CSS: {e}")

    def _update_preview_geometry(self):
        w = self.config.geometry.get("width", 400)
        h = self.config.geometry.get("height", 160)
        self.preview_card.set_size_request(w, h)

    def _recreate_preview(self):
        # Remove old
        parent = self.preview_card.get_parent() 
        # parent is CenterBox
        if parent:
            parent.set_center_widget(None)
        
        self.preview_card = DownloadCard(
            filename="invoice_2024.pdf", 
            size_human="2.4 MB",
            time_left=45,
            content_config=self.config.content
        )
        self.preview_card.set_valign(Gtk.Align.CENTER)
        self.preview_card.set_halign(Gtk.Align.CENTER)
        self._update_preview_geometry()
        
        parent.set_center_widget(self.preview_card)


class PreferencesApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.fabian.download_organizer.prefs", flags=0)

    def do_activate(self):
        win = PreferencesWindow(self)
        win.present()

if __name__ == "__main__":
    app = PreferencesApp()
    app.run(sys.argv)
