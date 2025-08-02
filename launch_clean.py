#!/usr/bin/env python3
"""
Clean launcher for EvolDSL Frontend with port conflict handling
"""

import subprocess
import sys
import time
import webbrowser
import socket
from pathlib import Path

def is_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def find_available_port(start_port, max_attempts=10):
    """Find an available port starting from start_port"""
    for i in range(max_attempts):
        port = start_port + i
        if is_port_available(port):
            return port
    return None

def kill_processes_on_port(port):
    """Kill processes running on a specific port"""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                subprocess.run(['kill', '-9', pid], capture_output=True)
            print(f"✅ Cleaned up processes on port {port}")
    except Exception as e:
        print(f"⚠️  Could not clean port {port}: {e}")

def main():
    print("🧬 EvolDSL Professional Frontend - Clean Launch")
    print("=" * 60)
    
    # Clean up potential conflicts
    print("🧹 Cleaning up any existing processes...")
    kill_processes_on_port(3000)
    kill_processes_on_port(8000)
    time.sleep(2)
    
    # Find available ports
    backend_port = find_available_port(8000)
    frontend_port = find_available_port(3000)
    
    if not backend_port or not frontend_port:
        print("❌ Could not find available ports. Please check your system.")
        return
    
    print(f"📡 Backend will use port: {backend_port}")
    print(f"🎨 Frontend will use port: {frontend_port}")
    
    # Update frontend to use correct backend port if different
    if backend_port != 8000:
        print(f"🔧 Updating frontend to use backend port {backend_port}...")
        # We'll use environment variable for this
    
    print("\n🚀 Starting EvolDSL...")
    
    # Start backend
    print(f"📡 Starting backend on http://localhost:{backend_port}...")
    backend_env = dict(os.environ) if 'os' in globals() else {}
    backend_env['PORT'] = str(backend_port)
    
    backend_process = subprocess.Popen([
        sys.executable, "backend_simple.py"
    ], env=backend_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for backend
    time.sleep(4)
    
    # Start frontend
    print(f"🎨 Starting frontend on http://localhost:{frontend_port}...")
    frontend_env = dict(os.environ) if 'os' in globals() else {}
    frontend_env['PORT'] = str(frontend_port)
    if backend_port != 8000:
        frontend_env['VITE_API_URL'] = f'http://localhost:{backend_port}'
    
    frontend_process = subprocess.Popen([
        'npm', 'run', 'dev', '--', '--port', str(frontend_port)
    ], cwd='frontend', env=frontend_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for frontend
    time.sleep(6)
    
    print("\n🎉 EvolDSL is ready!")
    print("=" * 60)
    print(f"🌐 Frontend: http://localhost:{frontend_port}")
    print(f"🔌 Backend:  http://localhost:{backend_port}")
    print("🔑 Your GPT-4o API key is pre-configured!")
    print("💡 Click 'Start Evolution' to begin the demo")
    print("=" * 60)
    
    # Open browser
    try:
        webbrowser.open(f'http://localhost:{frontend_port}')
        print("🌐 Opening browser...")
    except Exception:
        print("⚠️  Could not auto-open browser")
    
    print("\n🛑 Press Enter to stop all servers...")
    
    try:
        input()
    except KeyboardInterrupt:
        pass
    
    print("\n🛑 Stopping servers...")
    
    # Stop processes
    try:
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for graceful shutdown
        backend_process.wait(timeout=5)
        frontend_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        # Force kill if needed
        backend_process.kill()
        frontend_process.kill()
    except Exception as e:
        print(f"⚠️  Error stopping processes: {e}")
    
    print("✅ All servers stopped. Thank you!")

if __name__ == "__main__":
    import os
    main()