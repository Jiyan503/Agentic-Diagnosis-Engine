"""Configuration management for Dev Diagnosis."""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

APP_NAME = "Dev Diagnosis"
APP_VERSION = "1.0.0"

def get_asset_path(filename: str) -> Path:
    """Resolve asset path whether running as script or bundled in PyInstaller exe."""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent
    return base / "assets" / filename

# Storage path in AppData or fallback to local
def get_config_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        config_dir = Path(appdata) / "DevDiagnosis"
    else:
        config_dir = Path.home() / ".devdiagnosis"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

CONFIG_FILE = get_config_dir() / "settings.json"
HISTORY_DIR = get_config_dir() / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG: Dict[str, Any] = {
    "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
    "selected_model": "gemini-3.8-flash",
    "theme_mode": "Dark",
    "thoroughness_mode": "Deep Forensic Mode",
    "temperature": 0.2,
    "remember_key": True,
}

SUPPORTED_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-4-argon",
]

THOROUGHNESS_LEVELS = [
    "Deep Forensic Mode",
    "Exhaustive Audit",
    "Standard Triage",
]

def load_config() -> Dict[str, Any]:
    """Load configuration from disk with defaults fallback."""
    cfg = DEFAULT_CONFIG.copy()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                cfg.update(saved)
        except Exception:
            pass
    if not cfg["gemini_api_key"] and os.environ.get("GEMINI_API_KEY"):
        cfg["gemini_api_key"] = os.environ["GEMINI_API_KEY"]
    return cfg

def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to disk."""
    try:
        to_save = config.copy()
        if not to_save.get("remember_key", True):
            to_save["gemini_api_key"] = ""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def test_gemini_connection(api_key: str, model: str = "gemini-3.8-flash") -> tuple[bool, str]:
    """Instantaneous API key authentication and model verification via Google API gateway (<500ms)."""
    if not api_key or not api_key.strip():
        return False, "API key cannot be empty."

    clean_key = api_key.strip()
    try:
        from google import genai
        client = genai.Client(api_key=clean_key)
        model_info = client.models.get(model=model)
        display_name = getattr(model_info, 'display_name', None) or getattr(model_info, 'name', model)
        return True, f"API Key verified successfully with Google!\n\nEndpoint: {display_name}\nStatus: Active and ready for multi-agent diagnosis."
    except Exception as e:
        err = str(e)
        if any(x in err for x in ["API_KEY_INVALID", "400", "403", "PERMISSION_DENIED"]):
            return False, f"Authentication Failed: The provided key was rejected by Google.\n\nDetails: {err}"
        return False, f"Connection verification error: {err}"
