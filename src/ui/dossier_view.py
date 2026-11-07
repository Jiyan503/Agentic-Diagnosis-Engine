"""Rendered view for the comprehensive Diagnostic Dossier with export actions."""

import os
from typing import Dict, Any, Optional
from tkinter import filedialog, messagebox
import customtkinter as ctk

from src.ui.theme import Theme
from src.utils.exporter import export_to_markdown, export_to_html, export_to_json

class DossierView(ctk.CTkFrame):
    """View rendering the final synthesized Diagnostic Dossier."""

    def __init__(self, master, on_save_to_history=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.current_dossier: Optional[Dict[str, Any]] = None
        self.on_save_to_history = on_save_to_history

        self._build_ui()

    def _build_ui(self):
        # 1. Top Verdict Banner
        self.banner = ctk.CTkFrame(self, fg_color=Theme.BG_SECONDARY, corner_radius=10, border_width=1, border_color=Theme.BORDER)
        self.banner.pack(fill="x", padx=4, pady=(0, 10))

        banner_inner = ctk.CTkFrame(self.banner, fg_color="transparent")
        banner_inner.pack(fill="x", padx=16, pady=12)

        # Top row: Pills (Verdict, Confidence, Domain)
        pills_row = ctk.CTkFrame(banner_inner, fg_color="transparent")
        pills_row.pack(fill="x", pady=(0, 6))

        self.verdict_pill = ctk.CTkLabel(
            pills_row,
            text="VERDICT: PENDING AUDIT",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#3B1C1D",
            text_color="#FF7B72",
            corner_radius=4,
            padx=10,
            pady=3
        )
        self.verdict_pill.pack(side="left", padx=(0, 8))

        self.conf_pill = ctk.CTkLabel(
            pills_row,
            text="CONFIDENCE: --%",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#103623",
            text_color="#7EE787",
            corner_radius=4,
            padx=10,
            pady=3
        )
        self.conf_pill.pack(side="left", padx=(0, 8))

        self.domain_pill = ctk.CTkLabel(
            pills_row,
            text="DOMAIN: GENERAL",
            font=ctk.CTkFont(size=11),
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_MUTED,
            corner_radius=4,
            padx=8,
            pady=3
        )
        self.domain_pill.pack(side="left")

        # Elapsed & Model tag
        self.meta_lbl = ctk.CTkLabel(
            pills_row,
            text="Model: gemini-3.8-flash • Elapsed: 0.0s",
            font=ctk.CTkFont(size=11),
            text_color=Theme.TEXT_MUTED
        )
        self.meta_lbl.pack(side="right")

        # Verdict headline
        self.verdict_headline = ctk.CTkLabel(
            banner_inner,
            text="No diagnosis completed yet. Run a diagnosis to inspect results.",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
            wraplength=850,
            justify="left"
        )
        self.verdict_headline.pack(fill="x", pady=(4, 0))

        # 2. Main Tabview for Sections
        self.tabview = ctk.CTkTabview(self, fg_color=Theme.BG_SECONDARY, corner_radius=10, border_width=1, border_color=Theme.BORDER)
        self.tabview.pack(fill="both", expand=True, padx=4, pady=4)

        self.tab_rca = self.tabview.add("🔍 Root Cause Analysis")
        self.tab_fix = self.tabview.add("🔧 Actionable Fix & Patch")
        self.tab_verif = self.tabview.add("🧪 Verification Plan")
        self.tab_agents = self.tabview.add("👥 Specialist Agent Breakdown")

        # Tab 1: RCA Textbox
        self.rca_textbox = ctk.CTkTextbox(
            self.tab_rca,
            fg_color=Theme.TERMINAL_BG,
            text_color=Theme.TERMINAL_TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            wrap="word"
        )
        self.rca_textbox.pack(fill="both", expand=True, padx=8, pady=8)

        # Tab 2: Fix & Patch Textbox
        self.fix_textbox = ctk.CTkTextbox(
            self.tab_fix,
            fg_color=Theme.TERMINAL_BG,
            text_color=Theme.TERMINAL_TEXT,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none"
        )
        self.fix_textbox.pack(fill="both", expand=True, padx=8, pady=8)

        # Tab 3: Verification Textbox
        self.verif_textbox = ctk.CTkTextbox(
            self.tab_verif,
            fg_color=Theme.TERMINAL_BG,
            text_color=Theme.TERMINAL_TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            wrap="word"
        )
        self.verif_textbox.pack(fill="both", expand=True, padx=8, pady=8)

        # Tab 4: Specialist Agent Reports Textbox
        self.agents_textbox = ctk.CTkTextbox(
            self.tab_agents,
            fg_color=Theme.TERMINAL_BG,
            text_color=Theme.TERMINAL_TEXT,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word"
        )
        self.agents_textbox.pack(fill="both", expand=True, padx=8, pady=8)

        # 3. Action Toolbar (Copy, Export Markdown, Export HTML, Save)
        action_bar = ctk.CTkFrame(self, fg_color=Theme.BG_SECONDARY, corner_radius=10, border_width=1, border_color=Theme.BORDER)
        action_bar.pack(fill="x", padx=4, pady=(6, 0))

        bar_inner = ctk.CTkFrame(action_bar, fg_color="transparent")
        bar_inner.pack(fill="x", padx=16, pady=8)

        self.copy_fix_btn = ctk.CTkButton(
            bar_inner,
            text="📋 Copy Fix to Clipboard",
            height=30,
            fg_color=Theme.ACCENT_CYAN,
            hover_color=Theme.ACCENT_CYAN_HOVER,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._copy_fix
        )
        self.copy_fix_btn.pack(side="left", padx=(0, 8))

        self.export_md_btn = ctk.CTkButton(
            bar_inner,
            text="📄 Export Markdown (.md)",
            height=30,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_PRIMARY,
            hover_color=Theme.BG_CARD_HOVER,
            font=ctk.CTkFont(size=11),
            command=self._export_markdown
        )
        self.export_md_btn.pack(side="left", padx=4)

        self.export_html_btn = ctk.CTkButton(
            bar_inner,
            text="🌐 Export HTML Report",
            height=30,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_PRIMARY,
            hover_color=Theme.BG_CARD_HOVER,
            font=ctk.CTkFont(size=11),
            command=self._export_html
        )
        self.export_html_btn.pack(side="left", padx=4)

        self.save_history_btn = ctk.CTkButton(
            bar_inner,
            text="💾 Save to History",
            height=30,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_PRIMARY,
            hover_color=Theme.BG_CARD_HOVER,
            font=ctk.CTkFont(size=11),
            command=self._save_to_history
        )
        self.save_history_btn.pack(side="right")

    def display_dossier(self, dossier: Dict[str, Any]):
        """Render the structured diagnostic dossier into the UI."""
        self.current_dossier = dossier

        verdict = dossier.get("verdict", "DIAGNOSIS COMPLETE")
        confidence = dossier.get("confidence", "90%")
        domain = dossier.get("domain", "General")
        elapsed = dossier.get("elapsed_seconds", 0)
        model = dossier.get("model", "gemini-3.8-flash")

        # Update Pills
        self.verdict_pill.configure(text=f"VERDICT: {verdict[:35]}...")
        self.conf_pill.configure(text=f"CONFIDENCE: {confidence}")
        self.domain_pill.configure(text=f"DOMAIN: {domain}")
        self.meta_lbl.configure(text=f"Model: {model} • Elapsed: {elapsed}s")

        self.verdict_headline.configure(text=verdict)

        # Tab 1: RCA
        self.rca_textbox.delete("1.0", "end")
        self.rca_textbox.insert("1.0", dossier.get("executive_summary", "No root cause summary available."))

        # Tab 2: Fix
        self.fix_textbox.delete("1.0", "end")
        self.fix_textbox.insert("1.0", dossier.get("remediation", "No remediation instructions available."))

        # Tab 3: Verification
        self.verif_textbox.delete("1.0", "end")
        self.verif_textbox.insert("1.0", dossier.get("verification_plan", "No verification plan available."))

        # Tab 4: Agent reports
        self.agents_textbox.delete("1.0", "end")
        agent_reports = dossier.get("agent_findings", {})
        combined_agents = []
        for k, v in agent_reports.items():
            combined_agents.append(f"==================== [AGENT: {k.upper()}] ====================\n{v}\n\n")
        self.agents_textbox.insert("1.0", "".join(combined_agents))

        # Switch to fix tab by default so user sees the solution
        self.tabview.set("🔧 Actionable Fix & Patch")

    def _copy_fix(self):
        if not self.current_dossier:
            return
        fix_text = self.current_dossier.get("remediation", "")
        if fix_text:
            self.clipboard_clear()
            self.clipboard_append(fix_text)
            messagebox.showinfo("Copied", "Actionable fix copied to clipboard!")

    def _export_markdown(self):
        if not self.current_dossier:
            messagebox.showwarning("No Data", "No diagnostic dossier available to export.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md")],
            title="Export Diagnostic Dossier as Markdown"
        )
        if filepath:
            success = export_to_markdown(self.current_dossier, filepath)
            if success:
                messagebox.showinfo("Exported", f"Successfully exported Markdown report to:\n{filepath}")

    def _export_html(self):
        if not self.current_dossier:
            messagebox.showwarning("No Data", "No diagnostic dossier available to export.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html")],
            title="Export Diagnostic Dossier as Standalone HTML"
        )
        if filepath:
            success = export_to_html(self.current_dossier, filepath)
            if success:
                messagebox.showinfo("Exported", f"Successfully exported HTML report to:\n{filepath}")

    def _save_to_history(self):
        if not self.current_dossier:
            return
        if self.on_save_to_history:
            self.on_save_to_history(self.current_dossier)
            messagebox.showinfo("Saved", "Diagnostic dossier saved to history archive!")
