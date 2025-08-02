#!/usr/bin/env python3
"""
Quick demo launcher for EvolDSL Frontend
"""

import webbrowser
import time
import subprocess
import sys
from pathlib import Path

def main():
    print("🧬 EvolDSL Professional Frontend Demo")
    print("=" * 50)
    print("🚀 Starting servers...")
    
    # Start backend
    print("📡 Backend starting on http://localhost:8000...")
    backend_process = subprocess.Popen([
        sys.executable, "backend_simple.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for backend to start
    time.sleep(3)
    
    # Start frontend
    print("🎨 Frontend starting on http://localhost:3000...")
    frontend_process = subprocess.Popen([
        'npm', 'run', 'dev'
    ], cwd='frontend', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for frontend to start
    time.sleep(5)
    
    print("\n🎉 EvolDSL is ready!")
    print("=" * 50)
    print("🌐 Opening http://localhost:3000...")
    print("🔑 Your API key is pre-configured!")
    print("💡 Click 'Start Evolution' to see the demo")
    print("=" * 50)
    
    # Open browser
    webbrowser.open('http://localhost:3000')
    
    print("🛑 Press Enter to stop servers...")
    input()
    
    # Stop servers
    print("🛑 Stopping servers...")
    backend_process.terminate()
    frontend_process.terminate()
    
    backend_process.wait()
    frontend_process.wait()
    
    print("✅ Demo stopped. Thank you!")

if __name__ == "__main__":
    main()