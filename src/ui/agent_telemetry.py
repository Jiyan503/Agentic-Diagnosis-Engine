"""Live agent telemetry panel with status cards, stopwatch, and streaming logs."""

import time
from typing import Dict, Any
import customtkinter as ctk

from src.ui.theme import Theme

AGENT_META = [
    {
        "id": "triage",
        "name": "Agent 1: Triage Deconstructor",
        "desc": "Input ingestion, symptom deconstruction & specialist routing",
        "icon": "🧭"
    },
    {
        "id": "logic",
        "name": "Agent 2: Logic & Path Inspector",
        "desc": "AST data-flow, race conditions, memory locks, circuit netlist flow",
        "icon": "🧩"
    },
    {
        "id": "forensic",
        "name": "Agent 3: Multimodal Forensic Analyst",
        "desc": "Visual PCB inspection, video boot dynamics, acoustic noise FFT",
        "icon": "🔍"
    },
    {
        "id": "stress",
        "name": "Agent 4: Resilience & Stress Auditor",
        "desc": "Thermal runaway, ESD/overvoltage, CWE/OWASP, fault tolerance",
        "icon": "🛡️"
    },
    {
        "id": "synthesizer",
        "name": "Agent 5: Master Synthesizer",
        "desc": "Cross-verification, false positive elimination, exact remediation patch",
        "icon": "⚡"
    }
]

class AgentTelemetryView(ctk.CTkFrame):
    """Panel displaying real-time agent execution telemetry."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.agent_cards: Dict[str, Dict[str, Any]] = {}
        self.start_timestamp: float = 0.0
        self.timer_running: bool = False

        self._build_ui()

    def _build_ui(self):
        # 1. Top Bar: Progress bar + Stopwatch Timer + Stage Label
        top_bar = ctk.CTkFrame(self, fg_color=Theme.BG_SECONDARY, corner_radius=10, border_width=1, border_color=Theme.BORDER)
        top_bar.pack(fill="x", padx=4, pady=(0, 8))

        top_inner = ctk.CTkFrame(top_bar, fg_color="transparent")
        top_inner.pack(fill="x", padx=16, pady=10)

        # Stage label
        self.stage_lbl = ctk.CTkLabel(
            top_inner,
            text="Agent Orchestration: Ready",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_ACCENT
        )
        self.stage_lbl.pack(side="left")

        # Elapsed Timer label
        self.timer_lbl = ctk.CTkLabel(
            top_inner,
            text="⏱️ Elapsed: 00:00",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color=Theme.TEXT_MUTED
        )
        self.timer_lbl.pack(side="right")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            top_bar,
            height=8,
            corner_radius=4,
            progress_color=Theme.ACCENT_CYAN,
            fg_color=Theme.BG_PRIMARY
        )
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 10))
        self.progress_bar.set(0.0)

        # 2. Agent Cards Grid
        cards_container = ctk.CTkFrame(self, fg_color="transparent")
        cards_container.pack(fill="x", padx=0, pady=4)
        cards_container.columnconfigure((0, 1, 2, 3, 4), weight=1)

        for i, meta in enumerate(AGENT_META):
            card = ctk.CTkFrame(
                cards_container,
                fg_color=Theme.BG_SECONDARY,
                corner_radius=8,
                border_width=1,
                border_color=Theme.BORDER
            )
            card.grid(row=0, column=i, padx=3, pady=2, sticky="nsew")

            # Agent title
            ctk.CTkLabel(
                card,
                text=f"{meta['icon']} {meta['name'].split(':')[0]}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=Theme.TEXT_PRIMARY
            ).pack(anchor="w", padx=8, pady=(6, 1))

            # Role subtitle
            ctk.CTkLabel(
                card,
                text=meta["name"].split(":")[1].strip(),
                font=ctk.CTkFont(size=9),
                text_color=Theme.TEXT_MUTED
            ).pack(anchor="w", padx=8, pady=(0, 4))

            # Status Badge
            badge = ctk.CTkLabel(
                card,
                text="IDLE",
                font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                fg_color=Theme.BG_PRIMARY,
                text_color=Theme.TEXT_MUTED,
                corner_radius=4,
                width=65,
                height=18
            )
            badge.pack(anchor="w", padx=8, pady=(2, 6))

            self.agent_cards[meta["id"]] = {
                "frame": card,
                "badge": badge,
                "meta": meta
            }

        # 3. Live Streaming Terminal Logs
        terminal_frame = ctk.CTkFrame(self, fg_color=Theme.BG_SECONDARY, corner_radius=10, border_width=1, border_color=Theme.BORDER)
        terminal_frame.pack(fill="both", expand=True, padx=4, pady=(6, 0))

        term_header = ctk.CTkFrame(terminal_frame, fg_color="transparent")
        term_header.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            term_header,
            text="🖥️ Live Multi-Agent Diagnostic Telemetry Stream",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")

        clear_logs_btn = ctk.CTkButton(
            term_header,
            text="Clear Stream",
            width=80,
            height=20,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_MUTED,
            font=ctk.CTkFont(size=9),
            command=self.clear_logs
        )
        clear_logs_btn.pack(side="right")

        self.terminal_box = ctk.CTkTextbox(
            terminal_frame,
            fg_color=Theme.TERMINAL_BG,
            text_color=Theme.TERMINAL_TEXT,
            font=ctk.CTkFont(family="Consolas", size=10),
            border_width=1,
            border_color=Theme.BORDER
        )
        self.terminal_box.pack(fill="both", expand=True, padx=12, pady=(4, 10))

    def reset(self):
        """Reset all agent badges and progress."""
        for card in self.agent_cards.values():
            card["badge"].configure(text="IDLE", fg_color=Theme.BG_PRIMARY, text_color=Theme.TEXT_MUTED)
        self.progress_bar.set(0.0)
        self.stage_lbl.configure(text="Agent Orchestration: Ingestion Phase...", text_color=Theme.TEXT_ACCENT)
        self.start_timer()

    def set_agent_status(self, agent_id: str, status: str):
        """Update badge for a specific agent."""
        # Map common names
        agent_id_clean = agent_id.lower()
        target_key = None
        for k in self.agent_cards.keys():
            if k in agent_id_clean:
                target_key = k
                break
        
        if not target_key and "triage" in agent_id_clean:
            target_key = "triage"
        elif not target_key and "logic" in agent_id_clean:
            target_key = "logic"
        elif not target_key and "forensic" in agent_id_clean:
            target_key = "forensic"
        elif not target_key and "stress" in agent_id_clean:
            target_key = "stress"
        elif not target_key and "synthes" in agent_id_clean:
            target_key = "synthesizer"

        if target_key and target_key in self.agent_cards:
            badge = self.agent_cards[target_key]["badge"]
            badge.configure(text=status.upper())
            if "THINK" in status.upper() or "ACTIVE" in status.upper():
                badge.configure(fg_color="#0D3859", text_color="#00E5FF")
            elif "COMPLET" in status.upper() or "DONE" in status.upper() or "SUCCESS" in status.upper():
                badge.configure(fg_color="#0E3D24", text_color="#10B981")
            elif "ERROR" in status.upper():
                badge.configure(fg_color="#4C1517", text_color="#EF4444")
            else:
                badge.configure(fg_color=Theme.BG_PRIMARY, text_color=Theme.TEXT_MUTED)

    def log_event(self, source: str, message: str, level: str = "INFO"):
        """Append log event to the telemetry terminal."""
        ts = time.strftime("%H:%M:%S")
        prefix = f"[{ts}] [{source.upper()}]"
        
        # Colorize prefix or status
        line = f"{prefix} {message}\n"
        self.terminal_box.insert("end", line)
        self.terminal_box.see("end")

        # Automatically update agent badge if status was logged
        if level == "STATUS":
            self.set_agent_status(source, message.replace("Status changed to: ", ""))

    def update_progress(self, progress: float, stage_text: str):
        self.progress_bar.set(progress)
        self.stage_lbl.configure(text=f"Agent Orchestration: {stage_text}")

    def clear_logs(self):
        self.terminal_box.delete("1.0", "end")

    # Stopwatch Timer
    def start_timer(self):
        self.start_timestamp = time.time()
        self.timer_running = True
        self._tick_timer()

    def stop_timer(self):
        self.timer_running = False

    def _tick_timer(self):
        if not self.timer_running:
            return
        elapsed = int(time.time() - self.start_timestamp)
        mins, secs = divmod(elapsed, 60)
        self.timer_lbl.configure(text=f"⏱️ Elapsed: {mins:02d}:{secs:02d}")
        self.after(1000, self._tick_timer)
