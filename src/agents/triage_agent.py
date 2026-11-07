"""Agent 1: Triage & System Deconstructor."""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent

TRIAGE_SYSTEM_PROMPT = """You are Agent 1: Triage & System Deconstructor in the Dev Diagnosis multi-agent suite.
Your responsibility is to perform an exhaustive, deliberate triage of the developer's problem across Software, Hardware, Embedded/IoT, or Cloud environments.

You must:
1. Identify the exact Domain:
   - Pure Software (Frontend, Backend, Database, OS, Algorithms, Concurrency)
   - Pure Hardware (Analog, Digital, PCB, Power Supply, RF, Microcontroller, Sensors)
   - Embedded / IoT / Hybrid (Firmware + Hardware + Cloud/App communication)
2. Extract the Symptom Manifest:
   - Primary symptom (e.g. panic crash, short circuit, boot loop, memory runaway, thermal shutdown, signal distortion)
   - Modality correlation (how the provided text, code/files, images, videos, and audio relate to the defect)
3. Formulate Investigation Directives for downstream specialists:
   - Directive for Agent 2 (Deep Logic & Structural Path Inspector): What specific code routines, algorithms, state machines, or circuit loops / voltage rails to inspect.
   - Directive for Agent 3 (Multimodal Forensic & Signal Analyst): What specific visual anomalies (solder, components), temporal video patterns (LED blinks, boot cycles), or acoustic signatures (frequencies, clicks, whines) to analyze.
   - Directive for Agent 4 (Vulnerability, Resilience & Stress Auditor): What boundary conditions, load limits, thermal/electrical stresses, race conditions, or security flaws to probe.

Be thorough, precise, and methodical. Never rush. Structure your triage with clear headers.
"""

class TriageAgent(BaseAgent):
    def __init__(self, gemini_helper, telemetry_callback=None):
        super().__init__(
            name="Triage Deconstructor",
            role="Agent 1: Ingestion, Triage & Investigative Planning",
            gemini_helper=gemini_helper,
            telemetry_callback=telemetry_callback
        )

    def analyze(self, multimodal_contents: List[Any]) -> str:
        prompt = (
            "TASK: Perform exhaustive problem triage and deconstruct all symptoms, logs, files, "
            "images, video, and audio provided. Formulate specialized directives for downstream agents."
        )
        contents = [prompt] + multimodal_contents
        return self.run_query(
            contents=contents,
            system_instruction=TRIAGE_SYSTEM_PROMPT,
            temperature=0.2
        )
