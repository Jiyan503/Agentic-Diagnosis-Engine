"""Exporter for diagnostic reports (Markdown, standalone styled HTML, JSON)."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

def export_to_markdown(dossier: Dict[str, Any], filepath: str) -> bool:
    """Export diagnostic dossier to a clean Markdown file."""
    try:
        md = []
        md.append(f"# 🛠️ Dev Diagnosis Report")
        md.append(f"**Date:** {dossier.get('timestamp', datetime.now().isoformat())}")
        md.append(f"**Target Domain:** {dossier.get('domain', 'General System')}")
        md.append(f"**Verdict:** `{dossier.get('verdict', 'DIAGNOSIS COMPLETE')}`")
        md.append(f"**Diagnostic Confidence:** {dossier.get('confidence', '90%')}")
        md.append(f"**Model Used:** {dossier.get('model', 'gemini-3.8-flash')}")
        md.append("\n---\n")

        # Executive Summary
        md.append("## 📋 Executive Summary & Root Cause Analysis")
        md.append(dossier.get("executive_summary", "No summary provided."))
        md.append("\n---\n")

        # Primary Fix / Remediation
        md.append("## 🔧 Actionable Fix / Remediation")
        md.append(dossier.get("remediation", "No remediation provided."))
        md.append("\n---\n")

        # Individual Agent Analysis
        md.append("## 🔬 Specialized Agent Multi-Perspective Findings")
        
        agents = dossier.get("agent_findings", {})
        if "triage" in agents:
            md.append("### 🧭 Agent 1: System Triage & Problem Decomposition")
            md.append(agents["triage"])
            md.append("")
        
        if "logic" in agents:
            md.append("### 🧩 Agent 2: Deep Logic & Structural Path Inspector")
            md.append(agents["logic"])
            md.append("")
            
        if "forensic" in agents:
            md.append("### 🔍 Agent 3: Multimodal Forensic & Signal Analyst")
            md.append(agents["forensic"])
            md.append("")
            
        if "stress" in agents:
            md.append("### 🛡️ Agent 4: Vulnerability, Resilience & Stress Auditor")
            md.append(agents["stress"])
            md.append("")

        md.append("\n---\n")
        md.append("## 🧪 Verification & Prevention Guide")
        md.append(dossier.get("verification_plan", "No verification plan provided."))
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(md))
        return True
    except Exception as e:
        print(f"Failed to export markdown: {e}")
        return False

def export_to_html(dossier: Dict[str, Any], filepath: str) -> bool:
    """Export diagnostic dossier to an aesthetic standalone HTML report."""
    try:
        verdict = dossier.get("verdict", "DIAGNOSIS COMPLETE")
        confidence = dossier.get("confidence", "90%")
        domain = dossier.get("domain", "General")
        timestamp = dossier.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        model = dossier.get("model", "gemini-3.8-flash")
        
        def format_html_text(text: str) -> str:
            # Simple markdown-to-html converter for common formatting
            import html
            safe = html.escape(text)
            # Code blocks
            parts = safe.split("```")
            out = []
            for i, part in enumerate(parts):
                if i % 2 == 1:
                    # check if language is specified
                    lines = part.split("\n", 1)
                    lang = lines[0].strip() if len(lines) > 1 else ""
                    code = lines[1] if len(lines) > 1 else part
                    out.append(f'<pre><code class="code-block">{code}</code></pre>')
                else:
                    p_formatted = part.replace("\n\n", "</p><p>").replace("\n", "<br>")
                    # bold
                    import re
                    p_formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p_formatted)
                    p_formatted = re.sub(r'`(.*?)`', r'<code>\1</code>', p_formatted)
                    out.append(f"<p>{p_formatted}</p>")
            return "".join(out)

        exec_summary_html = format_html_text(dossier.get("executive_summary", ""))
        remediation_html = format_html_text(dossier.get("remediation", ""))
        verification_html = format_html_text(dossier.get("verification_plan", ""))

        agent_findings = dossier.get("agent_findings", {})
        agent_sections = ""
        agent_titles = [
            ("triage", "🧭 Agent 1: Triage & Decomposition"),
            ("logic", "🧩 Agent 2: Deep Logic & Structural Path"),
            ("forensic", "🔍 Agent 3: Multimodal Forensic & Signal"),
            ("stress", "🛡️ Agent 4: Vulnerability & Resilience Auditor")
        ]
        for key, title in agent_titles:
            if key in agent_findings:
                content = format_html_text(agent_findings[key])
                agent_sections += f"""
                <div class="agent-card">
                    <div class="agent-title">{title}</div>
                    <div class="agent-body">{content}</div>
                </div>
                """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dev Diagnosis Report - {verdict}</title>
<style>
  :root {{
    --bg: #0D1117;
    --card-bg: #161B22;
    --border: #30363D;
    --text-primary: #C9D1D9;
    --text-heading: #58A6FF;
    --accent: #00F0FF;
    --accent-glow: rgba(0, 240, 255, 0.2);
    --code-bg: #0A0D12;
    --badge-critical: #F85149;
    --badge-success: #3FB950;
  }}
  body {{
    background-color: var(--bg);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 30px 20px;
  }}
  .container {{
    max-width: 960px;
    margin: 0 auto;
  }}
  .header {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
  }}
  .header h1 {{
    margin: 0 0 10px 0;
    color: #FFFFFF;
    font-size: 26px;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .meta-pills {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 14px;
  }}
  .pill {{
    background: #21262D;
    border: 1px solid var(--border);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
  }}
  .pill-verdict {{
    background: rgba(248, 81, 73, 0.2);
    border-color: var(--badge-critical);
    color: #FF7B72;
    font-weight: bold;
  }}
  .pill-conf {{
    background: rgba(63, 185, 80, 0.2);
    border-color: var(--badge-success);
    color: #7EE787;
  }}
  .section {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
  }}
  .section h2 {{
    color: var(--text-heading);
    margin-top: 0;
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    font-size: 20px;
  }}
  .code-block {{
    background: var(--code-bg);
    border: 1px solid #2A303C;
    border-radius: 8px;
    padding: 16px;
    display: block;
    overflow-x: auto;
    font-family: "JetBrains Mono", Consolas, Courier New, monospace;
    font-size: 13px;
    color: #E6EDF3;
  }}
  code {{
    background: #21262D;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: Consolas, monospace;
  }}
  .agent-card {{
    background: #0D1117;
    border: 1px solid #30363D;
    border-radius: 8px;
    margin-bottom: 16px;
    padding: 16px;
  }}
  .agent-title {{
    font-weight: bold;
    color: var(--accent);
    margin-bottom: 8px;
  }}
  .footer {{
    text-align: center;
    color: #8B949E;
    font-size: 12px;
    margin-top: 40px;
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>⚡ Dev Diagnosis Dossier</h1>
    <div>Comprehensive AI Multi-Agent Software & Hardware Diagnostic Audit</div>
    <div class="meta-pills">
      <span class="pill pill-verdict">VERDICT: {verdict}</span>
      <span class="pill pill-conf">CONFIDENCE: {confidence}</span>
      <span class="pill">DOMAIN: {domain}</span>
      <span class="pill">MODEL: {model}</span>
      <span class="pill">DATE: {timestamp}</span>
    </div>
  </div>

  <div class="section">
    <h2>📋 Root Cause Analysis & Executive Findings</h2>
    {exec_summary_html}
  </div>

  <div class="section">
    <h2>🔧 Actionable Fix & Remediation Plan</h2>
    {remediation_html}
  </div>

  <div class="section">
    <h2>🔬 Multi-Agent Forensic Deep Dive</h2>
    {agent_sections}
  </div>

  <div class="section">
    <h2>🧪 Verification & Hardening Plan</h2>
    {verification_html}
  </div>

  <div class="footer">
    Generated by Dev Diagnosis Suite • Built with Google Gemini Multimodal Intelligence
  </div>
</div>
</body>
</html>
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        return True
    except Exception as e:
        print(f"Failed to export HTML: {e}")
        return False

def export_to_json(dossier: Dict[str, Any], filepath: str) -> bool:
    """Export diagnostic dossier to JSON."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dossier, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to export JSON: {e}")
        return False
