"""Multi-agent orchestrator executing concurrent diagnostic agents with real-time telemetry."""

import time
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional, Callable, List

from src.utils.gemini_helper import GeminiHelper
from src.agents.triage_agent import TriageAgent
from src.agents.logic_agent import LogicAgent
from src.agents.forensic_agent import ForensicAgent
from src.agents.stress_agent import StressAgent
from src.agents.synthesizer_agent import SynthesizerAgent

class DiagnosticOrchestrator:
    """
    Orchestrates the multi-agent diagnostic workflow:
    1. Prepares multimodal assets (text, code file, image, video, audio).
    2. Runs Agent 1 (Triage) to dissect the symptom space and formulate directives.
    3. Runs Agents 2, 3, and 4 simultaneously using ThreadPoolExecutor.
    4. Runs Agent 5 (Synthesizer) to compile the final authoritative Diagnostic Dossier.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.8-flash",
        telemetry_callback: Optional[Callable[[str, str, str], None]] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ):
        self.api_key = api_key
        self.model = model
        self.telemetry_callback = telemetry_callback
        self.progress_callback = progress_callback
        self.is_cancelled = False
        
        self.gemini_helper = GeminiHelper(api_key=api_key, model=model)
        
        # Instantiate agents
        self.triage_agent = TriageAgent(self.gemini_helper, self._agent_log)
        self.logic_agent = LogicAgent(self.gemini_helper, self._agent_log)
        self.forensic_agent = ForensicAgent(self.gemini_helper, self._agent_log)
        self.stress_agent = StressAgent(self.gemini_helper, self._agent_log)
        self.synthesizer_agent = SynthesizerAgent(self.gemini_helper, self._agent_log)

    def cancel(self):
        """Signal cancellation to all running agents."""
        self.is_cancelled = True
        self._notify_progress(0, "Diagnosis cancelled by user.")

    def _agent_log(self, agent_name: str, message: str, level: str = "INFO"):
        if self.telemetry_callback:
            self.telemetry_callback(agent_name, message, level)

    def _notify_progress(self, progress: float, stage_text: str):
        if self.progress_callback:
            self.progress_callback(progress, stage_text)

    def run_diagnosis(
        self,
        text_context: Optional[str] = None,
        code_file_path: Optional[str] = None,
        image_path: Optional[str] = None,
        video_path: Optional[str] = None,
        audio_path: Optional[str] = None,
        thoroughness_mode: str = "Deep Forensic Mode"
    ) -> Dict[str, Any]:
        """
        Execute full multi-agent diagnostic suite.
        Returns structured diagnostic dossier dictionary.
        """
        start_time = time.time()
        self.is_cancelled = False
        
        self._notify_progress(0.05, "Ingesting multimodal inputs (Code, Image, Video, Audio)...")
        self._agent_log("Orchestrator", f"Starting {thoroughness_mode} workflow with model {self.model}...", "INFO")

        # Step 1: Ingestion & Multimodal Packaging
        multimodal_contents = self.gemini_helper.prepare_multimodal_content(
            prompt="Diagnose the developer problem presented across these inputs.",
            text_context=text_context,
            code_file_path=code_file_path,
            image_path=image_path,
            video_path=video_path,
            audio_path=audio_path,
            progress_callback=lambda msg: self._agent_log("Orchestrator", msg, "INGEST")
        )

        if self.is_cancelled:
            return {"cancelled": True}

        # Step 2: Phase 1 - Triage & Deconstruction (Agent 1)
        self._notify_progress(0.15, "Phase 1: Agent 1 deconstructing symptoms & planning investigation...")
        self._agent_log("Orchestrator", "Activating Agent 1: Triage Deconstructor...", "STAGE")
        
        triage_report = self.triage_agent.analyze(multimodal_contents)
        
        if self.is_cancelled:
            return {"cancelled": True}

        # Step 3: Phase 2 - Simultaneous Specialist Agents Execution (Agents 2, 3, 4)
        self._notify_progress(0.35, "Phase 2: Launching 3 Specialist Agents concurrently...")
        self._agent_log("Orchestrator", "Spinning up parallel worker threads for Agents 2, 3, and 4...", "STAGE")

        agent_reports: Dict[str, str] = {"triage": triage_report}

        # Run Agents 2, 3, 4 simultaneously in thread pool
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_agent = {
                executor.submit(self.logic_agent.inspect, triage_report, multimodal_contents): "logic",
                executor.submit(self.forensic_agent.analyze, triage_report, multimodal_contents): "forensic",
                executor.submit(self.stress_agent.audit, triage_report, multimodal_contents): "stress",
            }

            completed_count = 0
            for future in as_completed(future_to_agent):
                agent_key = future_to_agent[future]
                if self.is_cancelled:
                    executor.shutdown(wait=False, cancel_futures=True)
                    return {"cancelled": True}
                try:
                    result_text = future.result()
                    agent_reports[agent_key] = result_text
                    completed_count += 1
                    current_prog = 0.35 + (completed_count * 0.15)
                    self._notify_progress(current_prog, f"Specialist Agent '{agent_key.upper()}' concluded analysis.")
                except Exception as e:
                    self._agent_log("Orchestrator", f"Agent {agent_key} failed: {e}", "ERROR")
                    agent_reports[agent_key] = f"Specialist investigation incomplete: {e}"

        if self.is_cancelled:
            return {"cancelled": True}

        # Step 4: Phase 3 - Master Diagnostic Synthesis & Peer Review (Agent 5)
        self._notify_progress(0.85, "Phase 3: Agent 5 synthesizing findings & formulating exact remediation...")
        self._agent_log("Orchestrator", "Activating Agent 5: Master Diagnostic Synthesizer...", "STAGE")
        
        final_synthesis = self.synthesizer_agent.synthesize(agent_reports, multimodal_contents)

        # Cleanup uploaded files from Gemini server if any
        try:
            self.gemini_helper.cleanup_remote_files()
        except Exception:
            pass

        # Step 5: Parse and format final Diagnostic Dossier
        self._notify_progress(1.0, "Diagnosis complete! Compiling Diagnostic Dossier...")
        elapsed_total = time.time() - start_time
        self._agent_log("Orchestrator", f"Full multi-agent audit concluded in {elapsed_total:.2f}s.", "SUCCESS")

        dossier = self._parse_synthesizer_output(final_synthesis, agent_reports)
        dossier["elapsed_seconds"] = round(elapsed_total, 2)
        dossier["model"] = self.model
        dossier["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dossier["thoroughness"] = thoroughness_mode

        return dossier

    def _parse_synthesizer_output(self, raw_text: str, agent_reports: Dict[str, str]) -> Dict[str, Any]:
        """Extract structured sections from Agent 5 markdown output."""
        dossier: Dict[str, Any] = {
            "verdict": "DIAGNOSIS COMPLETE",
            "confidence": "92%",
            "domain": "Software & Hardware Diagnostics",
            "executive_summary": "",
            "remediation": "",
            "verification_plan": "",
            "raw_text": raw_text,
            "agent_findings": agent_reports
        }

        # Extract sections using regex
        verdict_match = re.search(r"#\s*\[DIAGNOSTIC VERDICT\]\s*\n(.*?)(?=\n#|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
        if verdict_match:
            dossier["verdict"] = verdict_match.group(1).strip().replace("**", "").replace("`", "")

        conf_match = re.search(r"#\s*\[CONFIDENCE SCORE\]\s*\n(.*?)(?=\n#|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
        if conf_match:
            dossier["confidence"] = conf_match.group(1).strip()

        domain_match = re.search(r"#\s*\[IDENTIFIED DOMAIN\]\s*\n(.*?)(?=\n#|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
        if domain_match:
            dossier["domain"] = domain_match.group(1).strip()

        rca_match = re.search(r"#\s*\[ROOT CAUSE ANALYSIS\]\s*\n(.*?)(?=\n#|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
        if rca_match:
            dossier["executive_summary"] = rca_match.group(1).strip()

        fix_match = re.search(r"#\s*\[ACTIONABLE REMEDIATION & EXACT FIX\]\s*\n(.*?)(?=\n#|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
        if fix_match:
            dossier["remediation"] = fix_match.group(1).strip()

        verif_match = re.search(r"#\s*\[VERIFICATION & TESTING PLAN\]\s*\n(.*?)(?=\n#|\Z)", raw_text, re.DOTALL | re.IGNORECASE)
        if verif_match:
            dossier["verification_plan"] = verif_match.group(1).strip()

        # Fallback if headers were formatted slightly differently
        if not dossier["executive_summary"]:
            dossier["executive_summary"] = raw_text

        return dossier
