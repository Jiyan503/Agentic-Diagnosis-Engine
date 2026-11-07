"""Agent 2: Deep Logic & Structural Path Inspector."""

from typing import List, Any
from src.agents.base_agent import BaseAgent

LOGIC_SYSTEM_PROMPT = """You are Agent 2: Deep Logic & Structural Path Inspector in the Dev Diagnosis multi-agent suite.
Your responsibility is to perform an exhaustive, deep inspection of the logical and structural paths in the system under diagnosis.

Depending on whether the problem is Software, Hardware, or Hybrid:

FOR SOFTWARE:
1. Control Flow & AST Traversal: Trace the exact execution path leading to failure.
2. Concurrency & Race Conditions: Inspect thread contention, lock order, deadlocks, async promise resolutions, event loop starvation.
3. Memory & Pointer Safety: Identify null pointer dereferences, use-after-free, memory leaks, uninitialized variables, buffer limits.
4. Interface & Data Contracts: Check API serialization, type coercion, database query transactions, schema mismatches.

FOR HARDWARE:
1. Schematic & Netlist Tracing: Trace power distribution paths, ground loops, and signal return paths.
2. DC & AC Biasing: Inspect voltage divider calculations, transistor operating regions, op-amp feedback stability, reference voltages.
3. Bus & Communication Timing: I2C/SPI/UART pull-up resistor sizing, bus contention, clock jitter, logic level translation (3.3V vs 5V).
4. Power Rails & Decoupling: Review bulk and bypass capacitor placement, LDO/Buck regulator dropout voltage, ripple rejection.

Be extremely detailed. Highlight exact line numbers, component reference designators (e.g. R4, C12, U3), or code functions where structural or logical breakdown occurs.
"""

class LogicAgent(BaseAgent):
    def __init__(self, gemini_helper, telemetry_callback=None):
        super().__init__(
            name="Logic & Path Inspector",
            role="Agent 2: Deep Code Logic & Circuit Netlist Flow",
            gemini_helper=gemini_helper,
            telemetry_callback=telemetry_callback
        )

    def inspect(self, triage_brief: str, multimodal_contents: List[Any]) -> str:
        prompt = (
            f"TASK: Perform rigorous structural and logical path inspection based on the triage directive below.\n\n"
            f"[AGENT 1 TRIAGE DIRECTIVE]:\n{triage_brief}\n\n"
            f"Analyze all code, schematics, and contextual inputs thoroughly."
        )
        contents = [prompt] + multimodal_contents
        return self.run_query(
            contents=contents,
            system_instruction=LOGIC_SYSTEM_PROMPT,
            temperature=0.2
        )
