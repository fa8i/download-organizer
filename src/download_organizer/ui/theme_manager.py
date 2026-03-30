"""Theme Manager for dynamic UI customization."""

import json
import logging
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import DATA_DIR
ASSETS_DIR = Path(__file__).parent / "assets"

logger = logging.getLogger(__name__)

# Default Configuration
DEFAULT_CONFIG = {
    "geometry": {
        "width": 360,
        "height": 100
    },
    "appearance": {
        "font_family": "Sans",
        "bg_color": "#131116",
        "bg_opacity": 0.90,           # New: Glass Opacity
        
        "title_color": "#d0a0d4",
        "file_color": "#ffffff",
        "entry_text_color": "#ffffff",
        "button_text_color": "#ffffff",
        "subtext_color": "#7a6f8b",   # Internal/Static-ish
        
        "accent_color": "#9141ac",
        "accent_hover": "#9141ac",
        "button_bg": "#1a1223",
        "cancel_bg": "#2a2135", 
        "cancel_fg": "#ffffff",
        "entry_bg": "#241f31", 
        "border_color": "#2e213b",
        "border_radius": 15,
        "font_size_scale": 1.0,
    },
    "content": {
        "title_text": "Nueva descarga:",
        "placeholder_text": "Instrucción (Enter para auto)...",
        "btn_confirm": "Aceptar",
        "btn_cancel": "Cancelar"
    },
    "behavior": {
        "timeout": 5,
        "show_timer": True
    },
    "meta": {
        "theme_name": "Default Dark",
        "version": 5
    }
}

@dataclass
class ThemeConfig:
    geometry: Dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG["geometry"].copy())
    appearance: Dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG["appearance"].copy())
    content: Dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG["content"].copy())
    behavior: Dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG["behavior"].copy())
    meta: Dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG["meta"].copy())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeConfig':
        """Robustly load config, filling missing keys with defaults."""
        config = cls()
        
        # Merge dictionaries depth-1
        if "geometry" in data:
            config.geometry.update(data["geometry"])
        if "appearance" in data:
            config.appearance.update(data["appearance"])
        if "content" in data:
            config.content.update(data["content"])
        if "behavior" in data:
            config.behavior.update(data["behavior"])
        if "meta" in data:
            config.meta.update(data["meta"])
            
        return config

class ThemeManager:
    """Manages loading, saving, and generating CSS from theme configuration."""
    
    def __init__(self):
        self.config_path = DATA_DIR / "theme.json"
        self.config = self.load_config()

    def load_config(self) -> ThemeConfig:
        """Loads configuration from JSON file or returns default."""
        if not self.config_path.exists():
            logger.info("No theme file found, creating defaults.")
            default_config = ThemeConfig()
            self.save_config(default_config)
            return default_config
            
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                return ThemeConfig.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load theme config: {e}. Using defaults.")
            return ThemeConfig()

    def save_config(self, config: ThemeConfig):
        """Saves current configuration to JSON file."""
        self.config = config
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, 'w') as f:
                json.dump(asdict(config), f, indent=2)
            logger.info(f"Theme saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save theme config: {e}")

    def _hex_to_rgba(self, hex_color: str, alpha: float) -> str:
        """Converts hex color (#RRGGBB) to rgba(r, g, b, a)."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"rgba({r}, {g}, {b}, {alpha})"
        return hex_color

    def generate_css(self) -> str:
        """Generates GTK CSS string based on current configuration."""
        a = self.config.appearance
        
        # Helper to safely get values or defaults
        bg_hex = a.get("bg_color", "#131116")
        opacity = a.get("bg_opacity", 0.90)
        bg = self._hex_to_rgba(bg_hex, opacity)
        
        title_c = a.get("title_color", "#6233a3")
        file_c = a.get("file_color", "#e0d0f5")
        entry_text_c = a.get("entry_text_color", "#ffffff")
        btn_text_c = a.get("button_text_color", "#e0d0f5")
        sub_c = a.get("subtext_color", "#7a6f8b")
        
        btn_bg = a.get("button_bg", "#1a1223")

        cancel_bg = a.get("cancel_bg", "#2a2135")
        cancel_fg = a.get("cancel_fg", "#e0d0f5")
        
        entry_bg_hex = a.get("entry_bg", "#1a1223")
        entry_bg = self._hex_to_rgba(entry_bg_hex, opacity)
        
        accent = a.get("accent_color", "#6233a3")
        accent_hover = a.get("accent_hover", "#7b42cc")
        border = a.get("border_color", "#2e213b")
        radius = f"{a.get('border_radius', 12)}px"
        font_scale = f"{a.get('font_size_scale', 1.0)}em"
        font_family = a.get("font_family", "Sans")
        
        # NOTE: We scope everything to .main-window or specific classes to avoid leaking
        # into Preference Window UI which shares the same process/screen.
        css = f"""
        /* Clear window background and shadows for true transparency */
        window.transparent-window {{
            background-color: transparent;
            box-shadow: none;
            border: none;
        }}
        
        /* Ensure server-side decorations don't interfere */
        window.transparent-window > decoration {{
            box-shadow: none;
            background: none;
        }}

        .main-window {{
            background-color: {bg};
            /* Subtle reflective gradient for high-quality 'glossy' feel */
            background-image: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 50%, rgba(255, 255, 255, 0) 100%);
            
            color: {file_c};
            border-radius: {radius};
            
            /* High-quality glass border (simulating edge reflection) */
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            
            /* Deep, soft shadow for elevation */
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            
            padding: 20px;
            font-size: {font_scale};
            font-family: "{font_family}";
        }}
        /* Removed generic label selector to prevent leakage into buttons */
        
        .main-window .title {{ font-size: 1.25em; font-weight: 700; color: {title_c}; margin-bottom: 4px; }}
        .main-window .filename {{ font-size: 1.0em; font-weight: 600; color: {file_c}; margin-bottom: 2px; }}
        
        .main-window .subtitle {{ font-size: 0.85em; color: {sub_c}; margin-bottom: 15px; }}
        
        .main-window entry {{
            background-color: {entry_bg}; 
            color: {entry_text_c}; 
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px; 
            padding: 8px 12px; margin-bottom: 15px;
            caret-color: {accent}; 
            transition: all 200ms ease;
            background-image: none; /* Crucial for transparency */
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .main-window entry:focus {{ 
            border-color: {accent}; 
            background-color: shade({entry_bg}, 1.1); 
            box-shadow: 0 0 0 2px alpha({accent}, 0.3); 
        }}
        .main-window entry placeholder {{ color: alpha({entry_text_c}, 0.5); }}
        
        .main-window button {{
            background-color: {btn_bg}; 
            color: {btn_text_c}; 
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px; 
            padding: 6px 14px; 
            font-weight: 600;
            transition: all 200ms ease; 
            min-height: 28px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .main-window button:hover {{ 
            background-color: mix({btn_bg}, {file_c}, 0.9); 
            border-color: {file_c};
            color: {btn_text_c}; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .main-window button.suggested-action {{ 
            background-color: {btn_bg}; 
            color: {btn_text_c}; 
            border-color: rgba(255, 255, 255, 0.1); 
        }}
        .main-window button.suggested-action:hover {{ 
            background-color: {accent_hover}; 
            border-color: {accent_hover}; 
            box-shadow: 0 4px 12px alpha({accent}, 0.4); 
            color: {btn_text_c};
        }}
        
        .main-window button.cancel-action {{
            background-color: {cancel_bg};
            color: {cancel_fg};
            border-color: rgba(255, 255, 255, 0.05);
        }}
        .main-window button.cancel-action:hover {{
            background-color: shade({cancel_bg}, 1.1);
            color: {cancel_fg};
        }}
        
        .timer {{ font-size: 0.85em; color: {sub_c}; margin-top: 4px; }}
        .timer.warning {{ color: #f9a825; }}
        .timer.critical {{ color: #ef5350; }}
        """
        return css

