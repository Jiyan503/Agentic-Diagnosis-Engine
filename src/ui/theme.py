"""Theme definitions and color schemes for Dev Diagnosis."""

import customtkinter as ctk

class Theme:
    # Mode
    DARK = "Dark"
    LIGHT = "Light"

    # Color Palettes (Light, Dark) tuples for CustomTkinter
    BG_PRIMARY = ("#F8FAFC", "#0B0E14")
    BG_SECONDARY = ("#FFFFFF", "#151922")
    BG_CARD = ("#FFFFFF", "#1A202C")
    BG_CARD_HOVER = ("#EDF2F7", "#232A38")
    
    BORDER = ("#CBD5E1", "#2D3748")
    BORDER_ACCENT = ("#0284C7", "#00E5FF")

    TEXT_PRIMARY = ("#0F172A", "#F8FAFC")
    TEXT_MUTED = ("#64748B", "#94A3B8")
    TEXT_ACCENT = ("#0284C7", "#00E5FF")

    # Accent buttons & highlights
    ACCENT_CYAN = ("#0284C7", "#00E5FF")
    ACCENT_CYAN_HOVER = ("#0369A1", "#33EBFF")
    
    ACCENT_VIOLET = ("#7C3AED", "#A78BFA")
    ACCENT_VIOLET_HOVER = ("#6D28D9", "#C4B5FD")

    # Status colors
    STATUS_CRITICAL = ("#DC2626", "#EF4444")
    STATUS_WARNING = ("#D97706", "#F59E0B")
    STATUS_SUCCESS = ("#059669", "#10B981")
    STATUS_INFO = ("#2563EB", "#38BDF8")

    # Terminal / Code blocks
    TERMINAL_BG = ("#1E293B", "#080B10")
    TERMINAL_TEXT = ("#E2E8F0", "#38BDF8")

    @classmethod
    def apply_appearance(cls, mode: str):
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")
