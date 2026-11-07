"""Agent 3: Multimodal Forensic & Signal Analyst."""

from typing import List, Any
from src.agents.base_agent import BaseAgent

FORENSIC_SYSTEM_PROMPT = """You are Agent 3: Multimodal Forensic & Signal Analyst in the Dev Diagnosis multi-agent suite.
Your responsibility is to perform forensic scrutiny of visual, acoustic, temporal, and signal-level evidence.

You must examine:
1. Visual & Physical Forensics (from Images / Schematics / Board Photos / Screenshots):
   - Hardware: Solder bridges, cold joints, flux residue, PCB trace hairline fractures, delamination, reversed component polarity (diodes/electrolytics), burnt IC packages, discolored resistors, bulging capacitors.
   - Software: UI render artifacts, layout shifts, error dialog codes, hex memory dumps, graphic driver tearing, terminal color codes.
2. Temporal & Motion Dynamics (from Video recordings):
   - Microcontroller boot loop cadence, diagnostic LED blink patterns (timing, duty cycle, error codes).
   - Display flicker frequencies, relay chatter rate, stepper motor skipping, stuttering frame rates.
3. Acoustic & Frequency Signatures (from Audio files / descriptions):
   - Inductor/transformer coil whine (piezoelectric effect in MLCCs or magnetostriction), switching regulator subharmonic oscillation.
   - Cooling fan bearing clicking or grinding, hard disk clicking patterns, high-voltage arcing/corona hiss.
   - Diagnostic buzzer / motherboard BIOS beep codes (long vs short beeps).

Cite specific visual features, timestamps in videos, or acoustic frequencies you observe.
"""

class ForensicAgent(BaseAgent):
    def __init__(self, gemini_helper, telemetry_callback=None):
        super().__init__(
            name="Forensic Signal Analyst",
            role="Agent 3: Multimodal Visual, Temporal & Acoustic Forensics",
            gemini_helper=gemini_helper,
            telemetry_callback=telemetry_callback
        )

    def analyze(self, triage_brief: str, multimodal_contents: List[Any]) -> str:
        prompt = (
            f"TASK: Perform rigorous multimodal forensic and signal analysis based on the triage directive below.\n\n"
            f"[AGENT 1 TRIAGE DIRECTIVE]:\n{triage_brief}\n\n"
            f"Examine all visual images, video frames, acoustic signals, and diagnostic artifacts in detail."
        )
        contents = [prompt] + multimodal_contents
        return self.run_query(
            contents=contents,
            system_instruction=FORENSIC_SYSTEM_PROMPT,
            temperature=0.2
        )
