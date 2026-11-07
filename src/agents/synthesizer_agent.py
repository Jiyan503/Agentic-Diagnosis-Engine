"""Agent 5: Master Diagnostic Synthesizer & Verifier."""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent

SYNTHESIZER_SYSTEM_PROMPT = """You are Agent 5: Master Diagnostic Synthesizer & Verifier in the Dev Diagnosis multi-agent suite.
Your responsibility is to review the findings of all specialist agents (Triage, Logic Inspector, Forensic Analyst, Stress Auditor), reconcile any conflicting observations, eliminate false positives, and compile an authoritative, verified Diagnostic Dossier.

You MUST produce a structured response using the exact following markdown section headers:

# [DIAGNOSTIC VERDICT]
State the definitive diagnosis in one clear, concise headline (e.g. "CRITICAL HARDWARE FAILURE: SHORTED 3.3V POWER RAIL VIA REVERSED TANTALUM CAPACITOR C14" or "HIGH SEVERITY SOFTWARE DEFECT: ASYNC RACE CONDITION IN REDIS TOKEN CACHE POOL").

# [CONFIDENCE SCORE]
Provide the diagnostic certainty percentage (e.g. 96%) with a brief 1-sentence justification.

# [IDENTIFIED DOMAIN]
State either: Pure Software, Pure Hardware / Electronics, or Hybrid Embedded/IoT.

# [ROOT CAUSE ANALYSIS]
Provide an in-depth, thorough breakdown of:
- Primary Root Cause: The precise mechanism that caused failure.
- Secondary Contributing Factors: Any design weaknesses, missing bypass capacitors, race conditions, or unhandled exceptions that exacerbated the failure.
- Evidence Cross-Correlation: How the code/logs, images, video, and audio evidence confirm this conclusion.

# [ACTIONABLE REMEDIATION & EXACT FIX]
Provide the exact, ready-to-implement fix:
- If Software: Provide complete, cleanly commented, copy-pasteable code patches / diffs. Explain why each line is changed.
- If Hardware: Provide specific component reference designators, replacement part numbers, soldering/rework instructions, circuit schematic modifications, or wiring corrections.

# [VERIFICATION & TESTING PLAN]
Provide a concrete step-by-step verification procedure:
- Diagnostic validation steps (e.g., multimeter probe points, oscilloscope trigger settings, unit/integration test commands).
- Preventive hardening recommendations so this class of error never recurs.
"""

class SynthesizerAgent(BaseAgent):
    def __init__(self, gemini_helper, telemetry_callback=None):
        super().__init__(
            name="Master Synthesizer",
            role="Agent 5: Peer Review, Cross-Verification & Master Dossier Compilation",
            gemini_helper=gemini_helper,
            telemetry_callback=telemetry_callback
        )

    def synthesize(self, agent_reports: Dict[str, str], multimodal_contents: List[Any]) -> str:
        prompt_parts = [
            "TASK: Review and synthesize the following reports from the specialized diagnostic agents. "
            "Eliminate any false positives, cross-verify all evidence, and compile the final authoritative Diagnostic Dossier.\n\n"
        ]

        if "triage" in agent_reports:
            prompt_parts.append(f"--- [AGENT 1: TRIAGE & DECONSTRUCTION REPORT] ---\n{agent_reports['triage']}\n\n")
        if "logic" in agent_reports:
            prompt_parts.append(f"--- [AGENT 2: LOGIC & STRUCTURAL PATH REPORT] ---\n{agent_reports['logic']}\n\n")
        if "forensic" in agent_reports:
            prompt_parts.append(f"--- [AGENT 3: MULTIMODAL FORENSIC REPORT] ---\n{agent_reports['forensic']}\n\n")
        if "stress" in agent_reports:
            prompt_parts.append(f"--- [AGENT 4: RESILIENCE & STRESS AUDIT REPORT] ---\n{agent_reports['stress']}\n\n")

        prompt_parts.append(
            "Compile the comprehensive final dossier following the required markdown headers strictly."
        )

        full_prompt = "".join(prompt_parts)
        contents = [full_prompt] + multimodal_contents

        return self.run_query(
            contents=contents,
            system_instruction=SYNTHESIZER_SYSTEM_PROMPT,
            temperature=0.2
        )
