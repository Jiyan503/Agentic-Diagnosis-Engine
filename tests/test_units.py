"""Comprehensive unit test suite for Dev Diagnosis."""

import os
import json
import pytest
from pathlib import Path

from src.config import (
    load_config,
    save_config,
    SUPPORTED_MODELS,
    THOROUGHNESS_LEVELS,
    get_asset_path
)
from src.utils.file_helper import (
    get_file_category,
    get_file_mime,
    read_text_file,
    get_file_metadata
)
from src.utils.exporter import (
    export_to_markdown,
    export_to_html,
    export_to_json
)
from src.agents.orchestrator import DiagnosticOrchestrator

def test_config_defaults():
    cfg = load_config()
    assert "selected_model" in cfg
    assert cfg["selected_model"] in SUPPORTED_MODELS
    assert cfg["thoroughness_mode"] in THOROUGHNESS_LEVELS

def test_asset_path():
    ico = get_asset_path("app_icon.ico")
    assert ico.name == "app_icon.ico"
    assert ico.exists()

def test_file_helper_categories(tmp_path):
    py_file = tmp_path / "test.py"
    py_file.write_text("print('hello')", encoding="utf-8")
    assert get_file_category(str(py_file)) == "text"
    assert get_file_mime(str(py_file)) == "text/x-python"

    sch_file = tmp_path / "board.sch"
    sch_file.write_text("EESchema Schematic File Version 4", encoding="utf-8")
    assert get_file_category(str(sch_file)) == "text"

    meta = get_file_metadata(str(py_file))
    assert meta["exists"] is True
    assert meta["name"] == "test.py"

def test_file_helper_truncation(tmp_path):
    log_file = tmp_path / "huge_crash.log"
    # Write 2000 lines
    lines = [f"Log entry line {i}: debugging state info\n" for i in range(2000)]
    log_file.write_text("".join(lines), encoding="utf-8")

    content, truncated = read_text_file(str(log_file), max_lines=1500)
    assert truncated is True
    assert "TRUNCATED" in content
    assert "Log entry line 1999" in content

def test_exporters(tmp_path):
    sample_dossier = {
        "verdict": "CRITICAL POWER RAIL SHORT: REVERSED TANTALUM CAPACITOR C14",
        "confidence": "96%",
        "domain": "Pure Hardware / Electronics",
        "model": "gemini-3.8-flash",
        "elapsed_seconds": 12.4,
        "executive_summary": "Tantalum capacitor C14 placed backwards on 3.3V rail causing direct dead short to GND.",
        "remediation": "Desolder C14 with hot air rework at 350°C. Replace with 47uF 10V ceramic or orient tantalum polarity band to VOUT.",
        "verification_plan": "Measure resistance across 3.3V and GND before power. Verify >50k Ohms.",
        "agent_findings": {
            "triage": "Identified hardware overcurrent in CC mode.",
            "logic": "Traced 3.3V buck regulator net to C14.",
            "forensic": "Visual inspection shows polarity stripe reversed relative to silkscreen.",
            "stress": "Thermal runaway verified exceeding 115°C."
        }
    }

    md_path = tmp_path / "report.md"
    html_path = tmp_path / "report.html"
    json_path = tmp_path / "report.json"

    assert export_to_markdown(sample_dossier, str(md_path)) is True
    assert md_path.exists()
    assert "CRITICAL POWER RAIL SHORT" in md_path.read_text(encoding="utf-8")

    assert export_to_html(sample_dossier, str(html_path)) is True
    assert html_path.exists()
    assert "Dev Diagnosis Dossier" in html_path.read_text(encoding="utf-8")

    assert export_to_json(sample_dossier, str(json_path)) is True
    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
        assert loaded["confidence"] == "96%"

def test_orchestrator_parsing():
    orchestrator = DiagnosticOrchestrator(api_key="test_key_mock", model="gemini-3.8-flash")
    raw_synthesis = """# [DIAGNOSTIC VERDICT]
CRITICAL ASYNC DEADLOCK IN DISTRIBUTED TASK MANAGER

# [CONFIDENCE SCORE]
98% based on reverse lock acquisition order.

# [IDENTIFIED DOMAIN]
Pure Software

# [ROOT CAUSE ANALYSIS]
Function `update_task_state` acquires `lock_a` then `lock_b`.
Function `flush_and_snapshot` acquires `lock_b` then `lock_a`.
Under high concurrency, thread A holds `lock_a` waiting for `lock_b`, while thread B holds `lock_b` waiting for `lock_a`.

# [ACTIONABLE REMEDIATION & EXACT FIX]
Enforce consistent lock hierarchy: Always acquire `lock_a` before `lock_b`.
```python
async with self.lock_a:
    async with self.lock_b:
        # Critical section
```

# [VERIFICATION & TESTING PLAN]
Run stress test with 500 concurrent worker tasks.
"""
    reports = {
        "triage": "Identified lock contention",
        "logic": "Traced reverse acquisition order",
        "forensic": "Timeout stack trace confirmed",
        "stress": "Deadlock reproduces deterministically under 200+ rps"
    }

    dossier = orchestrator._parse_synthesizer_output(raw_synthesis, reports)
    assert "CRITICAL ASYNC DEADLOCK" in dossier["verdict"]
    assert "98%" in dossier["confidence"]
    assert dossier["domain"] == "Pure Software"
    assert "Reverse order" in dossier["executive_summary"] or "lock_a" in dossier["executive_summary"]
    assert "Enforce consistent lock hierarchy" in dossier["remediation"]
    assert len(dossier["agent_findings"]) == 4
