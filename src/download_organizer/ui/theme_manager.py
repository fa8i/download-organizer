"""Theme Manager for dynamic UI customization."""

import json
import logging
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import DATA_DIR

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

    def generate_css(self) -> str:
        """Generates GTK CSS string based on current configuration."""
        a = self.config.appearance
        
        # Helper to safely get values or defaults
        bg = a.get("bg_color", "#171421")
        
        title_c = a.get("title_color", "#6233a3")
        file_c = a.get("file_color", "#e0d0f5")
        entry_text_c = a.get("entry_text_color", "#ffffff")
        btn_text_c = a.get("button_text_color", "#e0d0f5")
        sub_c = a.get("subtext_color", "#7a6f8b")
        
        btn_bg = a.get("button_bg", "#1a1223")

        cancel_bg = a.get("cancel_bg", "#2a2135")
        cancel_fg = a.get("cancel_fg", "#e0d0f5")
        
        entry_bg = a.get("entry_bg", "#1a1223")
        
        accent = a.get("accent_color", "#6233a3")
        accent_hover = a.get("accent_hover", "#7b42cc")
        border = a.get("border_color", "#2e213b")
        radius = f"{a.get('border_radius', 12)}px"
        font_scale = f"{a.get('font_size_scale', 1.0)}em"
        font_family = a.get("font_family", "Sans")
        
        # NOTE: We scope everything to .main-window or specific classes to avoid leaking
        # into Preference Window UI which shares the same process/screen.
        css = f"""
        .transparent-window {{ 
            background-color: rgba(0,0,0,0); 
            box-shadow: none; 
            border: none; 
        }}
        
        .main-window {{
            background-color: {bg};
            color: {file_c};
            border-radius: {radius};
            border: 1px solid {border};
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
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
            border: 1px solid {border};
            border-radius: 6px; 
            padding: 8px 12px; margin-bottom: 15px;
            caret-color: {accent}; 
            transition: all 200ms ease;
        }}
        .main-window entry:focus {{ border-color: {accent}; background-color: shade({entry_bg}, 1.1); }}
        .main-window entry placeholder {{ color: alpha({entry_text_c}, 0.5); }}
        
        .main-window button {{
            background-color: {btn_bg}; 
            color: {btn_text_c}; 
            border: 1px solid {border};
            border-radius: 6px; 
            padding: 6px 14px; 
            font-weight: 600;
            transition: all 200ms ease; 
            min-height: 28px;
        }}
        .main-window button:hover {{ background-color: {border}; border-color: shade({border}, 1.1); color: {btn_text_c}; }}
        
        .main-window button.suggested-action {{ 
            background-color: {btn_bg}; 
            color: {btn_text_c}; 
            border-color: {btn_bg}; 
        }}
        .main-window button.suggested-action:hover {{ 
            background-color: {accent_hover}; 
            border-color: {accent_hover}; 
            box-shadow: 0 2px 8px alpha({accent}, 0.4); 
            color: {btn_text_c};
        }}

        .main-window button.cancel-action {{
            background-color: {cancel_bg};
            color: {cancel_fg};
            border-color: {border};
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

