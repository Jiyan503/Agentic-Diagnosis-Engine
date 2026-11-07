"""Base agent definition for Dev Diagnosis."""

import time
from typing import Callable, Optional, Dict, Any, List
from src.utils.gemini_helper import GeminiHelper

class BaseAgent:
    """Base class providing telemetry, logging, and Gemini model interaction for agents."""

    def __init__(
        self,
        name: str,
        role: str,
        gemini_helper: GeminiHelper,
        telemetry_callback: Optional[Callable[[str, str, str], None]] = None
    ):
        self.name = name
        self.role = role
        self.gemini_helper = gemini_helper
        self.telemetry_callback = telemetry_callback
        self.status = "IDLE"

    def log(self, message: str, level: str = "INFO"):
        """Send log message to UI telemetry."""
        if self.telemetry_callback:
            self.telemetry_callback(self.name, message, level)

    def set_status(self, status: str):
        """Update agent status."""
        self.status = status
        self.log(f"Status changed to: {status}", "STATUS")

    def run_query(
        self,
        contents: List[Any],
        system_instruction: str,
        temperature: float = 0.2
    ) -> str:
        """Execute query via Gemini Helper with retry and telemetry."""
        self.set_status("THINKING")
        self.log(f"Initiating deep diagnostic inquiry with {self.gemini_helper.model}...")
        
        start_time = time.time()
        try:
            result = self.gemini_helper.generate_with_retry(
                contents=contents,
                system_instruction=system_instruction,
                temperature=temperature,
                progress_callback=lambda msg: self.log(msg, "PROGRESS")
            )
            elapsed = time.time() - start_time
            self.log(f"Investigation complete in {elapsed:.2f}s.", "SUCCESS")
            self.set_status("COMPLETED")
            return result
        except Exception as e:
            self.log(f"Investigation encountered error: {str(e)}", "ERROR")
            self.set_status("ERROR")
            raise e
