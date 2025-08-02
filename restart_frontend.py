#!/usr/bin/env python3
"""
Quick script to restart just the frontend with fixed Tailwind config
"""

import subprocess
import sys
import time
import os
import signal

def kill_frontend():
    """Kill any running frontend processes"""
    try:
        result = subprocess.run(['lsof', '-ti', ':3000'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                subprocess.run(['kill', '-9', pid], capture_output=True)
            print("✅ Stopped existing frontend")
    except Exception as e:
        print(f"⚠️  Could not clean frontend: {e}")

def main():
    print("🔧 Restarting Frontend with Fixed Tailwind Config")
    print("=" * 50)
    
    # Stop any existing frontend
    kill_frontend()
    time.sleep(2)
    
    # Start frontend
    print("🎨 Starting frontend on http://localhost:3000...")
    
    os.chdir('frontend')
    
    try:
        # Start the frontend process
        process = subprocess.Popen(['npm', 'run', 'dev'])
        
        print("✅ Frontend restarted!")
        print("🌐 Visit: http://localhost:3000")
        print("🛑 Press Ctrl+C to stop")
        
        # Wait for process or Ctrl+C
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping frontend...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("✅ Frontend stopped")

if __name__ == "__main__":
    main()