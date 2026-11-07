"""Main desktop application window for Dev Diagnosis."""

import os
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import customtkinter as ctk
from PIL import Image

from src.ui.theme import Theme
from src.ui.header import HeaderView
from src.ui.input_panel import InputPanelView
from src.ui.agent_telemetry import AgentTelemetryView
from src.ui.dossier_view import DossierView
from src.ui.history_view import HistoryView
from src.config import load_config, save_config, HISTORY_DIR, get_asset_path
from src.agents.orchestrator import DiagnosticOrchestrator

class DevDiagnosisApp(ctk.CTk):
    """Main Application Window."""

    def __init__(self):
        super().__init__()
        self.config_data = load_config()

        # Apply initial appearance
        initial_theme = self.config_data.get("theme_mode", "Dark")
        Theme.apply_appearance(initial_theme)

        # Window settings
        self.title("Dev Diagnosis • AI Multi-Agent Diagnostic Suite")
        self.geometry("1180x820")
        self.minsize(1050, 700)

        # Set Window Icon
        self._set_app_icon()

        self.orchestrator: Optional[DiagnosticOrchestrator] = None
        self.worker_thread: Optional[threading.Thread] = None

        self._build_ui()

    def _set_app_icon(self):
        ico_path = get_asset_path("app_icon.ico")
        png_path = get_asset_path("app_logo.png")

        if ico_path.exists():
            try:
                self.iconbitmap(default=str(ico_path))
            except Exception:
                pass
        elif png_path.exists():
            try:
                img = Image.open(png_path)
                photo = ctk.CTkImage(img)
                self.iconphoto(False, photo)
            except Exception:
                pass

    def _build_ui(self):
        # Configure root layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Header View
        self.header = HeaderView(
            self,
            config=self.config_data,
            on_theme_toggle=self._handle_theme_change,
            on_config_change=self._handle_config_save
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))

        # 2. Workspace Navigation Tabs
        self.nav_tabview = ctk.CTkTabview(
            self,
            fg_color=Theme.BG_PRIMARY,
            corner_radius=10,
            border_width=1,
            border_color=Theme.BORDER
        )
        self.nav_tabview.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

        # Define tabs
        self.tab_input = self.nav_tabview.add("📥  Input Station")
        self.tab_telemetry = self.nav_tabview.add("⚡  Agent Telemetry & Live Console")
        self.tab_dossier = self.nav_tabview.add("📋  Diagnostic Dossier")
        self.tab_history = self.nav_tabview.add("📚  Audit History")

        # Tab 1: Input Station
        self.input_panel = InputPanelView(
            self.tab_input,
            on_start_diagnosis=self._start_diagnosis_flow,
            on_cancel_diagnosis=self._cancel_diagnosis_flow
        )
        self.input_panel.pack(fill="both", expand=True, padx=4, pady=4)

        # Tab 2: Agent Telemetry
        self.telemetry_view = AgentTelemetryView(self.tab_telemetry)
        self.telemetry_view.pack(fill="both", expand=True, padx=4, pady=4)

        # Tab 3: Diagnostic Dossier View
        self.dossier_view = DossierView(
            self.tab_dossier,
            on_save_to_history=self._save_dossier_to_history
        )
        self.dossier_view.pack(fill="both", expand=True, padx=4, pady=4)

        # Tab 4: Audit History
        self.history_view = HistoryView(
            self.tab_history,
            on_load_dossier=self._load_history_dossier
        )
        self.history_view.pack(fill="both", expand=True, padx=4, pady=4)

    def _handle_theme_change(self, mode: str):
        Theme.apply_appearance(mode)

    def _handle_config_save(self, updated_cfg: Dict[str, Any]):
        self.config_data = updated_cfg
        save_config(updated_cfg)

    def _start_diagnosis_flow(self, payload: Dict[str, Any]):
        """Initiate multi-agent workflow."""
        api_key = self.header.get_api_key()
        if not api_key:
            from tkinter import messagebox
            messagebox.showwarning(
                "Gemini API Key Missing",
                "Please enter your Gemini API Key in the top configuration bar before running diagnosis."
            )
            return

        model = self.header.get_selected_model()
        thoroughness = payload.get("thoroughness", "Deep Forensic Mode")

        # Update input panel states
        self.input_panel.set_running_state(True)

        # Reset telemetry view & switch to telemetry tab
        self.telemetry_view.reset()
        self.telemetry_view.log_event("App", f"Starting {thoroughness} with model: {model}...", "STAGE")
        self.nav_tabview.set("⚡  Agent Telemetry & Live Console")

        # Instantiate orchestrator
        self.orchestrator = DiagnosticOrchestrator(
            api_key=api_key,
            model=model,
            telemetry_callback=self._safe_telemetry_callback,
            progress_callback=self._safe_progress_callback
        )

        # Spawn background thread to keep UI completely fluid
        self.worker_thread = threading.Thread(
            target=self._run_diagnosis_worker,
            args=(payload, thoroughness),
            daemon=True
        )
        self.worker_thread.start()

    def _run_diagnosis_worker(self, payload: Dict[str, Any], thoroughness: str):
        try:
            dossier = self.orchestrator.run_diagnosis(
                text_context=payload.get("text"),
                code_file_path=payload.get("file_path"),
                image_path=payload.get("image_path"),
                video_path=payload.get("video_path"),
                audio_path=payload.get("audio_path"),
                thoroughness_mode=thoroughness
            )
            self.after(0, self._on_diagnosis_success, dossier)
        except Exception as e:
            self.after(0, self._on_diagnosis_error, str(e))

    def _safe_telemetry_callback(self, agent_name: str, message: str, level: str):
        # Dispatch to Tkinter main thread
        self.after(0, self.telemetry_view.log_event, agent_name, message, level)

    def _safe_progress_callback(self, progress: float, stage_text: str):
        self.after(0, self.telemetry_view.update_progress, progress, stage_text)

    def _on_diagnosis_success(self, dossier: Dict[str, Any]):
        self.input_panel.set_running_state(False)
        self.telemetry_view.stop_timer()

        if dossier.get("cancelled", False):
            self.telemetry_view.log_event("App", "Diagnosis was cancelled by user.", "WARNING")
            return

        self.telemetry_view.log_event("App", "Dossier compiled successfully!", "SUCCESS")
        
        # Render into DossierView
        self.dossier_view.display_dossier(dossier)

        # Auto-save to history
        self._save_dossier_to_history(dossier, silent=True)

        # Switch to Dossier Tab
        self.nav_tabview.set("📋  Diagnostic Dossier")

    def _on_diagnosis_error(self, error_message: str):
        self.input_panel.set_running_state(False)
        self.telemetry_view.stop_timer()
        self.telemetry_view.log_event("App", f"Diagnosis terminated due to error: {error_message}", "ERROR")
        
        from tkinter import messagebox
        messagebox.showerror("Diagnosis Error", f"An error occurred during diagnosis:\n\n{error_message}")

    def _cancel_diagnosis_flow(self):
        if self.orchestrator:
            self.orchestrator.cancel()
            self.input_panel.set_running_state(False)
            self.telemetry_view.stop_timer()

    def _save_dossier_to_history(self, dossier: Dict[str, Any], silent: bool = False):
        try:
            ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"diagnosis_{ts_str}.json"
            fpath = HISTORY_DIR / fname
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(dossier, f, indent=2)
            self.history_view.refresh_history()
        except Exception as e:
            if not silent:
                from tkinter import messagebox
                messagebox.showerror("Save Error", f"Could not save to history: {e}")

    def _load_history_dossier(self, dossier: Dict[str, Any]):
        self.dossier_view.display_dossier(dossier)
        self.nav_tabview.set("📋  Diagnostic Dossier")
