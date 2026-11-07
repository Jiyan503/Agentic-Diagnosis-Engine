"""History archive browser for past diagnostic audits."""

import json
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List
from tkinter import messagebox
import customtkinter as ctk

from src.ui.theme import Theme
from src.config import HISTORY_DIR

class HistoryView(ctk.CTkFrame):
    """View to browse and reload past saved diagnostic sessions."""

    def __init__(self, master, on_load_dossier: Callable[[Dict[str, Any]], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_load_dossier = on_load_dossier
        self.records: List[Dict[str, Any]] = []

        self._build_ui()
        self.refresh_history()

    def _build_ui(self):
        # Header bar
        header = ctk.CTkFrame(self, fg_color=Theme.BG_SECONDARY, corner_radius=10, border_width=1, border_color=Theme.BORDER)
        header.pack(fill="x", padx=4, pady=(0, 10))

        h_inner = ctk.CTkFrame(header, fg_color="transparent")
        h_inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(
            h_inner,
            text="📚 Diagnostic Archive & Audit History",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")

        refresh_btn = ctk.CTkButton(
            h_inner,
            text="🔄 Refresh",
            width=70,
            height=26,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_MUTED,
            font=ctk.CTkFont(size=10),
            command=self.refresh_history
        )
        refresh_btn.pack(side="right")

        # Scrollable container for history cards
        self.cards_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.cards_scroll.pack(fill="both", expand=True, padx=0, pady=0)

    def refresh_history(self):
        """Scan HISTORY_DIR and display cards."""
        for widget in self.cards_scroll.winfo_children():
            widget.destroy()

        self.records.clear()
        files = sorted(HISTORY_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)

        if not files:
            empty_lbl = ctk.CTkLabel(
                self.cards_scroll,
                text="No past diagnostic audits saved yet.\nCompleted audits can be saved using the 'Save to History' button in the Dossier view.",
                font=ctk.CTkFont(size=12),
                text_color=Theme.TEXT_MUTED,
                justify="center"
            )
            empty_lbl.pack(pady=40)
            return

        for fpath in files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["_filepath"] = str(fpath)
                self.records.append(data)
                self._create_history_card(data)
            except Exception:
                pass

    def _create_history_card(self, data: Dict[str, Any]):
        card = ctk.CTkFrame(self.cards_scroll, fg_color=Theme.BG_SECONDARY, corner_radius=8, border_width=1, border_color=Theme.BORDER)
        card.pack(fill="x", padx=4, pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        # Top row: timestamp + domain + confidence
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x", pady=(0, 4))

        ts = data.get("timestamp", "Unknown date")
        domain = data.get("domain", "General")
        conf = data.get("confidence", "90%")

        ctk.CTkLabel(
            top,
            text=f"📅 {ts}  •  🏷️ {domain}  •  🎯 {conf}",
            font=ctk.CTkFont(size=11),
            text_color=Theme.TEXT_MUTED
        ).pack(side="left")

        # Action buttons
        load_btn = ctk.CTkButton(
            top,
            text="Load Dossier",
            width=90,
            height=24,
            fg_color=Theme.ACCENT_CYAN,
            hover_color=Theme.ACCENT_CYAN_HOVER,
            font=ctk.CTkFont(size=10, weight="bold"),
            command=lambda d=data: self.on_load_dossier(d)
        )
        load_btn.pack(side="right", padx=(6, 0))

        del_btn = ctk.CTkButton(
            top,
            text="Delete",
            width=60,
            height=24,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.STATUS_CRITICAL,
            hover_color=Theme.BG_CARD_HOVER,
            font=ctk.CTkFont(size=10),
            command=lambda p=data.get("_filepath"): self._delete_record(p)
        )
        del_btn.pack(side="right")

        # Verdict headline
        verdict = data.get("verdict", "No verdict recorded.")
        ctk.CTkLabel(
            inner,
            text=verdict,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
            justify="left"
        ).pack(fill="x", pady=(2, 0))

    def _delete_record(self, filepath: Optional[str]):
        if not filepath:
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this diagnostic session from history?"):
            try:
                Path(filepath).unlink(missing_ok=True)
                self.refresh_history()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete record: {e}")
