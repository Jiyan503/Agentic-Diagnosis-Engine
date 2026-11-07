"""Dev Diagnosis - Entry point for the Windows desktop application."""

import sys
import os

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.app import DevDiagnosisApp

def main():
    app = DevDiagnosisApp()
    app.mainloop()

if __name__ == "__main__":
    main()
