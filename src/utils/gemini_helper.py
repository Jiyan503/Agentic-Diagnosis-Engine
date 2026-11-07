"""Gemini API payload and client helper with robust multimodal upload and backoff."""

import os
import time
import random
from typing import List, Any, Optional, Dict
from pathlib import Path
from google import genai
from google.genai import types

from src.utils.file_helper import get_file_category, get_file_mime, read_text_file

class GeminiHelper:
    """Manages Gemini API client, multimodal uploads, and retries."""
    
    def __init__(self, api_key: str, model: str = "gemini-3.8-flash"):
        self.api_key = api_key.strip()
        self.model = model
        self.client = genai.Client(api_key=self.api_key)
        self.uploaded_remote_files: List[Any] = []

    def prepare_multimodal_content(
        self,
        prompt: str,
        text_context: Optional[str] = None,
        code_file_path: Optional[str] = None,
        image_path: Optional[str] = None,
        video_path: Optional[str] = None,
        audio_path: Optional[str] = None,
        progress_callback: Optional[Any] = None
    ) -> List[Any]:
        """
        Package text, code files, images, videos, and audio into contents suitable
        for client.models.generate_content.
        """
        contents: List[Any] = []
        
        # 1. Primary prompt instructions
        contents.append(prompt)
        
        # 2. Text / Logs / Symptoms context
        if text_context and text_context.strip():
            contents.append(f"\n\n[USER PROVIDED LOGS / SYMPTOMS / CONTEXT]:\n```\n{text_context.strip()}\n```")
        
        # 3. Source Code / Configuration / Netlist file
        if code_file_path and os.path.exists(code_file_path):
            cat = get_file_category(code_file_path)
            file_name = Path(code_file_path).name
            if cat == "text":
                content_str, truncated = read_text_file(code_file_path)
                trunc_note = " (TRUNCATED FOR LENGTH)" if truncated else ""
                contents.append(f"\n\n[ATTACHED CODE/FILE: {file_name}{trunc_note}]:\n```\n{content_str}\n```")
            else:
                # Binary/other file -> upload to Files API or pass as bytes
                if progress_callback:
                    progress_callback(f"Uploading file '{file_name}' to Gemini API...")
                mime = get_file_mime(code_file_path)
                try:
                    with open(code_file_path, "rb") as f:
                        file_bytes = f.read()
                    contents.append(types.Part.from_bytes(data=file_bytes, mime_type=mime))
                except Exception as e:
                    contents.append(f"\n[Note: Could not read file {file_name}: {e}]")

        # 4. Image attachment (PCB photo, circuit schematic, error screenshot, waveform)
        if image_path and os.path.exists(image_path):
            img_name = Path(image_path).name
            if progress_callback:
                progress_callback(f"Preparing image '{img_name}' for visual inspection...")
            mime = get_file_mime(image_path)
            try:
                with open(image_path, "rb") as f:
                    img_bytes = f.read()
                contents.append(types.Part.from_bytes(data=img_bytes, mime_type=mime))
                contents.append(f"\n[IMAGE ATTACHED: {img_name} - Analyze visually for defects, circuit traces, components, or UI errors]")
            except Exception as e:
                contents.append(f"\n[Warning: Could not process image {img_name}: {e}]")

        # 5. Video attachment (Boot loop, blinking LED, motor behavior, error walkthrough)
        if video_path and os.path.exists(video_path):
            vid_name = Path(video_path).name
            if progress_callback:
                progress_callback(f"Uploading diagnostic video '{vid_name}' via Gemini Files API...")
            try:
                # Upload via Files API
                upload_res = self.client.files.upload(file=video_path)
                self.uploaded_remote_files.append(upload_res)
                
                # Check / wait for active state if needed
                state_name = getattr(upload_res.state, "name", str(upload_res.state))
                attempts = 0
                while state_name == "PROCESSING" and attempts < 15:
                    time.sleep(2)
                    attempts += 1
                    upload_res = self.client.files.get(name=upload_res.name)
                    state_name = getattr(upload_res.state, "name", str(upload_res.state))
                    if progress_callback:
                        progress_callback(f"Processing video frames on Gemini server ({attempts * 2}s)...")
                
                contents.append(upload_res)
                contents.append(f"\n[VIDEO ATTACHED: {vid_name} - Analyze temporal dynamics, blinking sequences, motion, and runtime behavior]")
            except Exception as e:
                contents.append(f"\n[Warning: Failed to upload video {vid_name}: {e}]")

        # 6. Audio attachment (Coil whine, relay clicks, fan noise, beep codes)
        if audio_path and os.path.exists(audio_path):
            aud_name = Path(audio_path).name
            if progress_callback:
                progress_callback(f"Preparing diagnostic audio '{aud_name}' for acoustic analysis...")
            mime = get_file_mime(audio_path)
            try:
                size_mb = os.path.getsize(audio_path) / (1024 * 1024)
                if size_mb < 15:
                    with open(audio_path, "rb") as f:
                        aud_bytes = f.read()
                    contents.append(types.Part.from_bytes(data=aud_bytes, mime_type=mime))
                else:
                    upload_res = self.client.files.upload(file=audio_path)
                    self.uploaded_remote_files.append(upload_res)
                    contents.append(upload_res)
                contents.append(f"\n[AUDIO ATTACHED: {aud_name} - Analyze acoustic frequencies, periodic clicks, pitch, or beep cadence]")
            except Exception as e:
                contents.append(f"\n[Warning: Failed to process audio {aud_name}: {e}]")

        return contents

    def generate_with_retry(
        self,
        contents: List[Any],
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_retries: int = 4,
        progress_callback: Optional[Any] = None
    ) -> str:
        """Call Gemini API with automatic exponential backoff for 429 rate limits, 503 high demand, and fallback models."""
        config_kwargs: Dict[str, Any] = {
            "temperature": temperature,
        }
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
            
        gen_config = types.GenerateContentConfig(**config_kwargs)

        # Candidate models list: primary selected model first, followed by resilient fallbacks
        fallback_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        models_queue = [self.model] + [m for m in fallback_models if m != self.model]

        for active_model in models_queue:
            delay = 2.0
            for attempt in range(1, max_retries + 1):
                try:
                    response = self.client.models.generate_content(
                        model=active_model,
                        contents=contents,
                        config=gen_config,
                    )
                    if response and response.text:
                        return response.text
                    return "No text response returned by model."
                except Exception as e:
                    err_msg = str(e)
                    is_rate_limit = "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "rate limit" in err_msg.lower()
                    is_high_demand = "503" in err_msg or "UNAVAILABLE" in err_msg or "high demand" in err_msg.lower()

                    if is_high_demand and attempt == max_retries and active_model != models_queue[-1]:
                        # Switch to next fallback model
                        if progress_callback:
                            progress_callback(
                                f"Model '{active_model}' is experiencing high demand on Google servers. "
                                f"Switching to resilient fallback model..."
                            )
                        break

                    if attempt == max_retries and active_model == models_queue[-1]:
                        raise RuntimeError(f"Gemini API request failed across models: {err_msg}")

                    wait_time = delay + random.uniform(0.5, 2.0)
                    if is_rate_limit or is_high_demand:
                        wait_time = max(wait_time, 4.0 * attempt)
                        if progress_callback:
                            status_label = "Google servers high demand (503)" if is_high_demand else "Rate limit"
                            progress_callback(f"{status_label}. Agent retrying in {wait_time:.1f}s (Attempt {attempt}/{max_retries})...")
                    else:
                        if progress_callback:
                            progress_callback(f"API transient glitch ({err_msg[:40]}...). Retrying in {wait_time:.1f}s...")

                    time.sleep(wait_time)
                    delay *= 1.8

        return "Failed to generate diagnosis."

    def cleanup_remote_files(self):
        """Clean up temporary files uploaded to Gemini server."""
        for f in self.uploaded_remote_files:
            try:
                self.client.files.delete(name=f.name)
            except Exception:
                pass
        self.uploaded_remote_files.clear()
