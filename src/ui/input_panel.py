"""Input station supporting multimodal text, code files, images, videos, and audio."""

import os
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

from src.ui.theme import Theme
from src.utils.file_helper import (
    get_file_metadata,
    TEXT_CODE_EXTENSIONS,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    AUDIO_EXTENSIONS
)
from src.config import THOROUGHNESS_LEVELS

PRESETS = {
    "Python Async Race Condition": {
        "text": """[CRITICAL CRASH REPORT]
Environment: Python 3.10 / FastAPI / Asyncpg / Redis
Symptom: Under 250 req/sec load, the microservice locks up completely. Worker processes become unresponsive, CPU hangs at 100%, and incoming requests fail with 'HTTP 504 Gateway Timeout'.
Stack Trace:
Traceback (most recent call last):
  File "workers/task_distributor.py", line 142, in process_batch
    await asyncio.wait_for(self.mutex.acquire(), timeout=5.0)
  File "asyncio/tasks.py", line 445, in wait_for
    raise exceptions.TimeoutError()
asyncio.exceptions.TimeoutError

Investigate potential deadlocks between task_distributor and cache invalidation routines.""",
        "code_content": """import asyncio
from typing import Dict, Any

class DistributedTaskManager:
    def __init__(self):
        self.lock_a = asyncio.Lock()
        self.lock_b = asyncio.Lock()
        self.registry: Dict[str, Any] = {}

    async def update_task_state(self, task_id: str, new_state: str):
        # Transaction 1: Acquires lock_a, then lock_b
        async with self.lock_a:
            await asyncio.sleep(0.01) # Simulated network I/O
            async with self.lock_b:
                self.registry[task_id] = new_state
                return True

    async def flush_and_snapshot(self):
        # Transaction 2: Acquires lock_b, then lock_a (Reverse order lock acquisition!)
        async with self.lock_b:
            await asyncio.sleep(0.01) # Simulated disk sync
            async with self.lock_a:
                snapshot = dict(self.registry)
                self.registry.clear()
                return snapshot
""",
        "category": "Software"
    },
    "PCB Power Rail Short & Blown Regulator": {
        "text": """[HARDWARE FAILURE REPORT]
Board: STM32 Custom Industrial Controller Rev 2.1
Input Voltage: 12V DC input via Barrel Jack J1
Symptoms:
- Upon applying 12V power, bench power supply immediately drops into Constant Current (CC) mode, drawing 2.5A at 1.4V.
- Step-down buck regulator U1 (TPS54302) gets scorching hot (>115°C) within 3 seconds.
- 3.3V rail reads only 0.42V.
- Multimeter continuity test between 3.3V power rail and GND shows 0.8 Ohms resistance (Dead Short).
- Tantalum capacitor C14 near the MCU feels warm.

Schematic excerpt:
U1 TPS54302: VIN pin 2 connected to 12V via ferrite bead FB1. SW pin 3 connected to 4.7uH Inductor L1.
Output capacitor bank: C12 (22uF Ceramic 10V), C14 (47uF Tantalum 6.3V SMD).
VOUT feedback network: R1=10k, R2=3.3k.

Please diagnose whether the failure is component breakdown, reverse polarity, or thermal runaway.""",
        "category": "Hardware"
    },
    "ESP32 Boot Loop with Blinking LED": {
        "text": """[EMBEDDED / FIRMWARE BOOT LOOP]
Hardware: ESP32-WROOM-32E custom breakout board.
Power: 3.3V via AMS1117-3.3 regulator powered from 5V USB.
Symptom:
- Built-in status LED flashes rapidly 3 times, pauses for 1 second, and repeats continuously.
- Serial monitor baud 115200 prints:
rst:0x10 (RTCWDT_RTC_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
configsip: 0, SPIWP:0xee
clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
mode:DIO, clock div:2
load:0x3fff0030,len:1184
load:0x40078000,len:13104
load:0x40080400,len:3036
entry 0x400805e4
Brownout detector was triggered
Guru Meditation Error: Core 0 panic'ed (Unhandled debug exception)

Please inspect the brownout trigger and decoupling capacitor sizing on the 3.3V rail.""",
        "category": "Hybrid"
    },
    "Switching PSU Coil Whine & Acoustic Noise": {
        "text": """[ACOUSTIC & THERMAL NOISE AUDIT]
Unit: 48V to 12V Synchronous Buck Converter for Server Rack.
Symptom:
- High-pitched piercing whine audible around 12kHz - 15kHz under light load (0.2A - 0.8A).
- Under heavy load (>5A), acoustic noise transitions to intermittent clicking/buzzing.
- Output voltage ripple spikes from 35mVpp up to 450mVpp at 14kHz.
- Switching MOSFET gate drive waveform on oscilloscope shows pulse skipping and irregular burst periods.
- Ceramic capacitor bank C8-C11 vibrating (piezoelectric resonance suspected).

Diagnose stability margin, phase margin, and recommend snubber or ceramic-to-electrolytic dampening.""",
        "category": "Hardware"
    }
}

class InputPanelView(ctk.CTkScrollableFrame):
    """Scrollable container for all developer diagnostic inputs."""

    def __init__(
        self,
        master,
        on_start_diagnosis: Callable[[Dict[str, Any]], None],
        on_cancel_diagnosis: Callable[[], None],
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_start_diagnosis = on_start_diagnosis
        self.on_cancel_diagnosis = on_cancel_diagnosis

        self.selected_file_path: Optional[str] = None
        self.selected_image_path: Optional[str] = None
        self.selected_video_path: Optional[str] = None
        self.selected_audio_path: Optional[str] = None

        self._build_ui()

    def _build_ui(self):
        # 1. Preset Bar
        preset_frame = ctk.CTkFrame(self, fg_color=Theme.BG_SECONDARY, corner_radius=8, border_width=1, border_color=Theme.BORDER)
        preset_frame.pack(fill="x", padx=4, pady=(0, 10))

        preset_lbl = ctk.CTkLabel(
            preset_frame,
            text="⚡ Quick Diagnosis Presets:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_ACCENT
        )
        preset_lbl.pack(side="left", padx=(12, 8), pady=8)

        for name in PRESETS.keys():
            btn = ctk.CTkButton(
                preset_frame,
                text=name.split(":")[0],
                width=110,
                height=26,
                fg_color=Theme.BG_PRIMARY,
                text_color=Theme.TEXT_PRIMARY,
                hover_color=Theme.BG_CARD_HOVER,
                font=ctk.CTkFont(size=10),
                command=lambda n=name: self._load_preset(n)
            )
            btn.pack(side="left", padx=4, pady=8)

        # 2. Section: Text / Logs / Symptoms (Core Text Input)
        text_section = ctk.CTkFrame(self, fg_color=Theme.BG_SECONDARY, corner_radius=10, border_width=1, border_color=Theme.BORDER)
        text_section.pack(fill="x", padx=4, pady=6)

        text_header = ctk.CTkFrame(text_section, fg_color="transparent")
        text_header.pack(fill="x", padx=12, pady=(10, 4))

        ctk.CTkLabel(
            text_header,
            text="📝 Symptoms, Stack Traces & Diagnostic Logs",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")

        clear_text_btn = ctk.CTkButton(
            text_header,
            text="Clear",
            width=50,
            height=22,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_MUTED,
            font=ctk.CTkFont(size=10),
            command=self._clear_text
        )
        clear_text_btn.pack(side="right", padx=4)

        paste_btn = ctk.CTkButton(
            text_header,
            text="Paste",
            width=50,
            height=22,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_MUTED,
            font=ctk.CTkFont(size=10),
            command=self._paste_text
        )
        paste_btn.pack(side="right", padx=4)

        self.symptom_textbox = ctk.CTkTextbox(
            text_section,
            height=130,
            fg_color=Theme.TERMINAL_BG,
            text_color=Theme.TERMINAL_TEXT,
            border_width=1,
            border_color=Theme.BORDER,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.symptom_textbox.pack(fill="x", padx=12, pady=(4, 12))
        self.symptom_textbox.insert(
            "1.0",
            "Paste crash tracebacks, error logs, hardware voltage readings, or defect symptoms here..."
        )

        # 3. Section: Multimodal Input Grid (Code File, Image, Video, Audio)
        media_grid = ctk.CTkFrame(self, fg_color="transparent")
        media_grid.pack(fill="x", padx=0, pady=4)
        media_grid.columnconfigure((0, 1), weight=1)

        # 3A: Code / Schematic / Netlist File Card
        self.file_card = self._create_attachment_card(
            parent=media_grid,
            row=0, col=0,
            icon="📄",
            title="Source Code / Netlist / Log File",
            supported_text=".py, .js, .cpp, .sch, .net, .log, .json...",
            browse_command=self._browse_code_file,
            clear_command=self._clear_code_file
        )

        # 3B: Image Card (PCB Photo / Schematic / Screenshot / Waveform)
        self.image_card = self._create_attachment_card(
            parent=media_grid,
            row=0, col=1,
            icon="🖼️",
            title="Image / PCB Photo / Waveform",
            supported_text=".png, .jpg, .webp (Circuit boards, oscilloscopes, errors)",
            browse_command=self._browse_image,
            clear_command=self._clear_image
        )

        # 3C: Video Card (Boot loops, blinking LEDs, motion, reproduction)
        self.video_card = self._create_attachment_card(
            parent=media_grid,
            row=1, col=0,
            icon="🎥",
            title="Video / Boot Sequence / LED Blink",
            supported_text=".mp4, .webm, .mov (Temporal dynamics, crash reproduction)",
            browse_command=self._browse_video,
            clear_command=self._clear_video
        )

        # 3D: Audio Card (Acoustic Noise, Whine, Beep Codes)
        self.audio_card = self._create_attachment_card(
            parent=media_grid,
            row=1, col=1,
            icon="🔊",
            title="Audio / Acoustic Noise / Beep Code",
            supported_text=".mp3, .wav, .ogg (Coil whine, fan chatter, BIOS beeps)",
            browse_command=self._browse_audio,
            clear_command=self._clear_audio
        )

        # 4. Thoroughness & Launch Bar
        launch_frame = ctk.CTkFrame(self, fg_color=Theme.BG_SECONDARY, corner_radius=10, border_width=1, border_color=Theme.BORDER)
        launch_frame.pack(fill="x", padx=4, pady=(10, 16))

        launch_inner = ctk.CTkFrame(launch_frame, fg_color="transparent")
        launch_inner.pack(fill="x", padx=16, pady=12)

        # Thoroughness Mode dropdown
        mode_box = ctk.CTkFrame(launch_inner, fg_color="transparent")
        mode_box.pack(side="left")

        ctk.CTkLabel(
            mode_box,
            text="Diagnostic Thoroughness:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 8))

        self.thoroughness_menu = ctk.CTkOptionMenu(
            mode_box,
            values=THOROUGHNESS_LEVELS,
            width=180,
            height=32,
            fg_color=Theme.BG_PRIMARY,
            button_color=Theme.ACCENT_CYAN,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.thoroughness_menu.set("Deep Forensic Mode")
        self.thoroughness_menu.pack(side="left")

        # Start Diagnosis Button
        self.start_btn = ctk.CTkButton(
            launch_inner,
            text="🚀  Start Multi-Agent Diagnosis",
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=Theme.ACCENT_CYAN,
            hover_color=Theme.ACCENT_CYAN_HOVER,
            command=self._trigger_start
        )
        self.start_btn.pack(side="right", padx=(8, 0))

        # Cancel Button
        self.cancel_btn = ctk.CTkButton(
            launch_inner,
            text="Cancel",
            height=38,
            width=80,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=Theme.STATUS_CRITICAL,
            command=self._trigger_cancel
        )
        # cancel button hidden initially
        self.cancel_btn.pack_forget()

    def _create_attachment_card(self, parent, row, col, icon, title, supported_text, browse_command, clear_command):
        card = ctk.CTkFrame(parent, fg_color=Theme.BG_SECONDARY, corner_radius=10, border_width=1, border_color=Theme.BORDER)
        card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

        # Top title
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            header,
            text=f"{icon} {title}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")

        # Subtitle / supported info
        ctk.CTkLabel(
            card,
            text=supported_text,
            font=ctk.CTkFont(size=9),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", padx=10, pady=(0, 4))

        # File display box
        status_box = ctk.CTkFrame(card, fg_color=Theme.BG_PRIMARY, corner_radius=6, border_width=1, border_color=Theme.BORDER)
        status_box.pack(fill="x", padx=10, pady=4)

        info_lbl = ctk.CTkLabel(
            status_box,
            text="No file attached",
            font=ctk.CTkFont(size=10),
            text_color=Theme.TEXT_MUTED
        )
        info_lbl.pack(side="left", padx=8, pady=4)

        # Action buttons
        btn_bar = ctk.CTkFrame(card, fg_color="transparent")
        btn_bar.pack(fill="x", padx=10, pady=(4, 8))

        browse_btn = ctk.CTkButton(
            btn_bar,
            text="Attach...",
            width=70,
            height=24,
            fg_color=Theme.ACCENT_CYAN,
            hover_color=Theme.ACCENT_CYAN_HOVER,
            font=ctk.CTkFont(size=10, weight="bold"),
            command=browse_command
        )
        browse_btn.pack(side="left")

        clear_btn = ctk.CTkButton(
            btn_bar,
            text="Remove",
            width=60,
            height=24,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_MUTED,
            font=ctk.CTkFont(size=10),
            command=clear_command
        )
        clear_btn.pack(side="left", padx=6)

        return {
            "card": card,
            "info_lbl": info_lbl,
            "status_box": status_box
        }

    # File browsing handlers
    def _browse_code_file(self):
        ext_filter = "Code & Log Files (*.*)|*.*"
        path = filedialog.askopenfilename(title="Select Code, Netlist or Log File")
        if path:
            self.selected_file_path = path
            meta = get_file_metadata(path)
            self.file_card["info_lbl"].configure(
                text=f"✓ {meta['name']} ({meta['size_formatted']})",
                text_color=Theme.STATUS_SUCCESS
            )

    def _clear_code_file(self):
        self.selected_file_path = None
        self.file_card["info_lbl"].configure(text="No file attached", text_color=Theme.TEXT_MUTED)

    def _browse_image(self):
        path = filedialog.askopenfilename(
            title="Select PCB, Circuit or Screenshot Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.gif")]
        )
        if path:
            self.selected_image_path = path
            meta = get_file_metadata(path)
            self.image_card["info_lbl"].configure(
                text=f"✓ {meta['name']} ({meta['size_formatted']})",
                text_color=Theme.STATUS_SUCCESS
            )

    def _clear_image(self):
        self.selected_image_path = None
        self.image_card["info_lbl"].configure(text="No image attached", text_color=Theme.TEXT_MUTED)

    def _browse_video(self):
        path = filedialog.askopenfilename(
            title="Select Video Recording",
            filetypes=[("Video files", "*.mp4;*.webm;*.mov;*.avi;*.mkv")]
        )
        if path:
            self.selected_video_path = path
            meta = get_file_metadata(path)
            self.video_card["info_lbl"].configure(
                text=f"✓ {meta['name']} ({meta['size_formatted']})",
                text_color=Theme.STATUS_SUCCESS
            )

    def _clear_video(self):
        self.selected_video_path = None
        self.video_card["info_lbl"].configure(text="No video attached", text_color=Theme.TEXT_MUTED)

    def _browse_audio(self):
        path = filedialog.askopenfilename(
            title="Select Diagnostic Audio Recording",
            filetypes=[("Audio files", "*.mp3;*.wav;*.ogg;*.aac;*.m4a")]
        )
        if path:
            self.selected_audio_path = path
            meta = get_file_metadata(path)
            self.audio_card["info_lbl"].configure(
                text=f"✓ {meta['name']} ({meta['size_formatted']})",
                text_color=Theme.STATUS_SUCCESS
            )

    def _clear_audio(self):
        self.selected_audio_path = None
        self.audio_card["info_lbl"].configure(text="No audio attached", text_color=Theme.TEXT_MUTED)

    def _clear_text(self):
        self.symptom_textbox.delete("1.0", "end")

    def _paste_text(self):
        try:
            clipboard = self.clipboard_get()
            self.symptom_textbox.insert("insert", clipboard)
        except Exception:
            pass

    def _load_preset(self, preset_name: str):
        preset = PRESETS.get(preset_name)
        if not preset:
            return
        self.symptom_textbox.delete("1.0", "end")
        self.symptom_textbox.insert("1.0", preset["text"].strip())

        # If preset has code content, write to temporary file and attach
        if "code_content" in preset:
            import tempfile
            tmp_dir = Path(tempfile.gettempdir()) / "dev_diagnosis_presets"
            tmp_dir.mkdir(exist_ok=True)
            tmp_file = tmp_dir / f"{preset_name.replace(' ', '_').lower()}.py"
            with open(tmp_file, "w", encoding="utf-8") as f:
                f.write(preset["code_content"])
            self.selected_file_path = str(tmp_file)
            meta = get_file_metadata(str(tmp_file))
            self.file_card["info_lbl"].configure(
                text=f"✓ {meta['name']} ({meta['size_formatted']})",
                text_color=Theme.STATUS_SUCCESS
            )

    def _trigger_start(self):
        text = self.symptom_textbox.get("1.0", "end").strip()
        has_file = bool(self.selected_file_path)
        has_image = bool(self.selected_image_path)
        has_video = bool(self.selected_video_path)
        has_audio = bool(self.selected_audio_path)

        if not text and not has_file and not has_image and not has_video and not has_audio:
            messagebox.showwarning(
                "Input Required",
                "Please provide at least one diagnostic input: symptom text, code/log file, image, video, or audio."
            )
            return

        payload = {
            "text": text,
            "file_path": self.selected_file_path,
            "image_path": self.selected_image_path,
            "video_path": self.selected_video_path,
            "audio_path": self.selected_audio_path,
            "thoroughness": self.thoroughness_menu.get()
        }
        self.on_start_diagnosis(payload)

    def _trigger_cancel(self):
        self.on_cancel_diagnosis()

    def set_running_state(self, is_running: bool):
        """Update button states during diagnosis."""
        if is_running:
            self.start_btn.configure(text="⏳  Diagnosis In Progress...", state="disabled")
            self.cancel_btn.pack(side="right", padx=(0, 8))
        else:
            self.start_btn.configure(text="🚀  Start Multi-Agent Diagnosis", state="normal")
            self.cancel_btn.pack_forget()
