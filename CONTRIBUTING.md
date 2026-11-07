# Contributing to Dev Diagnosis

Thank you for your interest in contributing to **Dev Diagnosis**! We welcome bug reports, feature suggestions, specialized diagnostic agents, and documentation improvements.

---

## 🛠️ Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/dev-diagnosis.git
   cd dev-diagnosis
   ```

2. **Create a virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the test suite**:
   ```powershell
   python -m pytest tests/test_units.py -v
   ```

---

## 🧠 Adding New Specialized Agents

To add a new specialized agent to the orchestration pipeline:
1. Subclass `BaseAgent` in `src/agents/`.
2. Implement your agent's domain prompt in `your_agent.py`.
3. Register the agent in `src/agents/orchestrator.py` and attach its metadata to `src/ui/agent_telemetry.py`.
4. Add unit test coverage in `tests/test_units.py`.

---

## 📦 Building the Windows Executable (.exe)

Compile the standalone executable using PyInstaller:
```powershell
pyinstaller --noconfirm DevDiagnosis.spec
```
The resulting executable will be placed in `dist/DevDiagnosis.exe`.

---

## 📜 Pull Request Guidelines

1. Ensure all tests in `tests/test_units.py` pass before opening a PR.
2. Maintain documentation integrity and update `README.md` or `ARCHITECTURE.md` if public interfaces or agent roles change.
3. Follow PEP 8 style conventions for Python code.
