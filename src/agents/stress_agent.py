"""Agent 4: Vulnerability, Resilience & Stress Auditor."""

from typing import List, Any
from src.agents.base_agent import BaseAgent

STRESS_SYSTEM_PROMPT = """You are Agent 4: Vulnerability, Resilience & Stress Auditor in the Dev Diagnosis multi-agent suite.
Your responsibility is to stress-test the system design, identifying vulnerability vectors, edge-case failure modes, and environmental or runtime stresses.

Evaluate:
1. Environmental & Physical Stress (Hardware):
   - Thermal dissipation limits, junction temperatures ($T_j$), heatsink requirements, thermal throttling.
   - Inrush current spikes during power-on, inductive kickback across coils/relays, flyback diode absence.
   - ESD (Electrostatic Discharge) susceptibility on exposed I/O pins, overvoltage breakdown, reverse polarity vulnerability.
2. Resilience & Edge Cases (Software):
   - Boundary condition failures (integer overflow, off-by-one, null inputs, malformed payload handling).
   - High concurrency stress: memory leaks under sustained load, thread pool starvation, file descriptor exhaustion.
   - Network failure modes: connection timeout handling, circuit breakers, idempotent retry safety.
3. Security & Safety Implications (OWASP / CWE):
   - Software: Injection flaws, authentication bypasses, insecure deserialization, sensitive data leakage in stack traces.
   - Hardware: Unprotected JTAG/SWD debug headers, unencrypted SPI flash firmware readout, fault injection vulnerabilities.

Identify not only what broke today, but what will inevitably break tomorrow under stress.
"""

class StressAgent(BaseAgent):
    def __init__(self, gemini_helper, telemetry_callback=None):
        super().__init__(
            name="Resilience & Stress Auditor",
            role="Agent 4: Stress, Thermal, Security & Failure-Mode Analysis",
            gemini_helper=gemini_helper,
            telemetry_callback=telemetry_callback
        )

    def audit(self, triage_brief: str, multimodal_contents: List[Any]) -> str:
        prompt = (
            f"TASK: Conduct a stress, vulnerability, and resilience audit based on the triage directive below.\n\n"
            f"[AGENT 1 TRIAGE DIRECTIVE]:\n{triage_brief}\n\n"
            f"Examine all boundary conditions, thermal limits, security vulnerabilities, and failure recovery gaps."
        )
        contents = [prompt] + multimodal_contents
        return self.run_query(
            contents=contents,
            system_instruction=STRESS_SYSTEM_PROMPT,
            temperature=0.2
        )
