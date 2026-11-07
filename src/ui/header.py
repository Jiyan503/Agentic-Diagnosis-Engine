"""Header bar containing logo, branding, theme switch, and Gemini API controls."""

import os
from pathlib import Path
from typing import Callable, Optional, Dict, Any
import customtkinter as ctk
from PIL import Image

from src.ui.theme import Theme
from src.config import SUPPORTED_MODELS, test_gemini_connection, get_asset_path

class HeaderView(ctk.CTkFrame):
    """Header bar with logo, theme toggle, and API key management."""

    def __init__(
        self,
        master,
        config: Dict[str, Any],
        on_theme_toggle: Callable[[str], None],
        on_config_change: Callable[[Dict[str, Any]], None],
        **kwargs
    ):
        super().__init__(master, fg_color=Theme.BG_SECONDARY, corner_radius=10, border_width=1, border_color=Theme.BORDER, **kwargs)
        self.config = config
        self.on_theme_toggle = on_theme_toggle
        self.on_config_change = on_config_change
        self.show_key = False

        self._build_ui()

    def _build_ui(self):
        # 1. Top row: Branding + Theme Switcher
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(12, 6))

        # Brand / Logo
        brand_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        brand_frame.pack(side="left", fill="y")

        logo_path = get_asset_path("app_logo.png")
        if logo_path.exists():
            try:
                pil_img = Image.open(logo_path)
                logo_ctk = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(42, 42))
                self.logo_label = ctk.CTkLabel(brand_frame, text="", image=logo_ctk)
                self.logo_label.pack(side="left", padx=(0, 10))
            except Exception:
                pass

        titles_frame = ctk.CTkFrame(brand_frame, fg_color="transparent")
        titles_frame.pack(side="left", fill="y")

        title_lbl = ctk.CTkLabel(
            titles_frame,
            text="DEV DIAGNOSIS",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=Theme.TEXT_ACCENT
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            titles_frame,
            text="AI Multi-Agent Diagnostic Suite • Software, Hardware & Multimodal Forensics",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Theme.TEXT_MUTED
        )
        subtitle_lbl.pack(anchor="w")

        # Right side: Theme switch
        theme_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        theme_frame.pack(side="right", padx=6)

        current_theme = self.config.get("theme_mode", "Dark")
        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Dark Mode" if current_theme == "Dark" else "Light Mode",
            command=self._handle_theme_toggle,
            onvalue="Dark",
            offvalue="Light",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        if current_theme == "Dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()
        self.theme_switch.pack(side="right")

        # 2. Bottom row: Gemini API Key & Model Configuration
        config_row = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=8, border_width=1, border_color=Theme.BORDER)
        config_row.pack(fill="x", padx=16, pady=(6, 12))

        # API Key Label
        key_lbl = ctk.CTkLabel(
            config_row,
            text="🔑 Gemini API Key:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        key_lbl.pack(side="left", padx=(12, 6), pady=8)

        # API Key Input
        self.key_entry = ctk.CTkEntry(
            config_row,
            placeholder_text="Enter your Gemini API key (AQ. or AIza...)",
            show="*",
            width=260,
            fg_color=Theme.BG_PRIMARY,
            border_color=Theme.BORDER,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        saved_key = self.config.get("gemini_api_key", "")
        if saved_key:
            self.key_entry.insert(0, saved_key)
        self.key_entry.pack(side="left", padx=(0, 6), pady=8)

        # Toggle visibility button
        self.toggle_eye_btn = ctk.CTkButton(
            config_row,
            text="👁",
            width=32,
            height=28,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_MUTED,
            hover_color=Theme.BG_CARD_HOVER,
            command=self._toggle_key_visibility
        )
        self.toggle_eye_btn.pack(side="left", padx=(0, 6), pady=8)

        # Test Connection button
        self.test_btn = ctk.CTkButton(
            config_row,
            text="Test Key",
            width=76,
            height=28,
            fg_color=Theme.ACCENT_CYAN,
            hover_color=Theme.ACCENT_CYAN_HOVER,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._handle_test_connection
        )
        self.test_btn.pack(side="left", padx=(0, 10), pady=8)

        # Model Selector
        model_lbl = ctk.CTkLabel(
            config_row,
            text="Model:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        model_lbl.pack(side="left", padx=(10, 6), pady=8)

        self.model_dropdown = ctk.CTkOptionMenu(
            config_row,
            values=SUPPORTED_MODELS,
            width=160,
            height=28,
            command=self._handle_model_change,
            fg_color=Theme.BG_PRIMARY,
            button_color=Theme.ACCENT_CYAN,
            button_hover_color=Theme.ACCENT_CYAN_HOVER,
            font=ctk.CTkFont(size=11)
        )
        current_model = self.config.get("selected_model", "gemini-3.8-flash")
        if current_model in SUPPORTED_MODELS:
            self.model_dropdown.set(current_model)
        self.model_dropdown.pack(side="left", padx=(0, 10), pady=8)

        # Status Label
        self.status_lbl = ctk.CTkLabel(
            config_row,
            text="Key saved" if saved_key else "Key required",
            font=ctk.CTkFont(size=11),
            text_color=Theme.STATUS_SUCCESS if saved_key else Theme.STATUS_WARNING
        )
        self.status_lbl.pack(side="left", padx=8, pady=8)

    def _toggle_key_visibility(self):
        self.show_key = not self.show_key
        self.key_entry.configure(show="" if self.show_key else "*")
        self.toggle_eye_btn.configure(text="🔒" if self.show_key else "👁")

    def _handle_theme_toggle(self):
        mode = self.theme_switch.get()
        self.theme_switch.configure(text=f"{mode} Mode")
        self.config["theme_mode"] = mode
        self.on_theme_toggle(mode)
        self.on_config_change(self.config)

    def _handle_model_change(self, selected_model: str):
        self.config["selected_model"] = selected_model
        self.on_config_change(self.config)

    def _handle_test_connection(self):
        import threading
        key = self.get_api_key()
        if not key:
            self.status_lbl.configure(text="Key required", text_color=Theme.STATUS_WARNING)
            from tkinter import messagebox
            messagebox.showwarning("Key Missing", "Please enter your Gemini API key in the field before testing.")
            return

        model = self.model_dropdown.get()
        self.test_btn.configure(text="⏳ Testing...", state="disabled")
        self.status_lbl.configure(text="Checking with Gemini...", text_color=Theme.STATUS_INFO)

        def worker():
            success, msg = test_gemini_connection(key, model)
            self.after(0, self._on_test_finished, success, msg, key)

        threading.Thread(target=worker, daemon=True).start()

    def _on_test_finished(self, success: bool, msg: str, key: str):
        self.test_btn.configure(text="Test Key", state="normal")
        if success:
            self.status_lbl.configure(text="✓ Connected to Gemini", text_color=Theme.STATUS_SUCCESS)
            self.config["gemini_api_key"] = key
            self.on_config_change(self.config)
            from tkinter import messagebox
            messagebox.showinfo("Gemini Connection Successful", msg)
        else:
            self.status_lbl.configure(text="✗ Connection Failed", text_color=Theme.STATUS_CRITICAL)
            from tkinter import messagebox
            messagebox.showerror("Gemini Connection Error", msg)

    def get_api_key(self) -> str:
        return self.key_entry.get().strip()

    def get_selected_model(self) -> str:
        return self.model_dropdown.get()
