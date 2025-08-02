#!/usr/bin/env python3
"""
Startup script for EvolDSL Professional Frontend
Starts both the backend API and frontend development server
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        print("✅ Python backend dependencies found")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("💡 Install with: pip install -r requirements_api.txt")
        return False
    
    # Check Node.js and npm
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} found")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        print("💡 Install Node.js from: https://nodejs.org/")
        return False
    
    # Check if frontend dependencies are installed
    frontend_path = Path(__file__).parent / "frontend"
    node_modules = frontend_path / "node_modules"
    
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(['npm', 'install'], cwd=frontend_path, check=True)
            print("✅ Frontend dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install frontend dependencies")
            return False
    else:
        print("✅ Frontend dependencies found")
    
    return True

def start_backend():
    """Start the backend API server"""
    print("🚀 Starting backend API server...")
    
    backend_script = Path(__file__).parent / "backend_simple.py"
    
    # Start the backend process
    backend_process = subprocess.Popen([
        sys.executable, str(backend_script)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Wait a moment for the server to start
    time.sleep(3)
    
    # Check if the process is still running
    if backend_process.poll() is None:
        print("✅ Backend API server started on http://localhost:8000")
        return backend_process
    else:
        stdout, stderr = backend_process.communicate()
        print(f"❌ Backend failed to start:")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return None

def start_frontend():
    """Start the frontend development server"""
    print("🎨 Starting frontend development server...")
    
    frontend_path = Path(__file__).parent / "frontend"
    
    # Start the frontend process
    frontend_process = subprocess.Popen([
        'npm', 'run', 'dev'
    ], cwd=frontend_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Wait a moment for the server to start
    time.sleep(5)
    
    # Check if the process is still running
    if frontend_process.poll() is None:
        print("✅ Frontend development server started on http://localhost:3000")
        return frontend_process
    else:
        stdout, stderr = frontend_process.communicate()
        print(f"❌ Frontend failed to start:")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return None

def main():
    """Main startup function"""
    print("🧬 EvolDSL Professional Frontend Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please resolve the issues above.")
        sys.exit(1)
    
    print("\n🔧 Starting services...")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend. Exiting.")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend. Stopping backend and exiting.")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 EvolDSL is ready!")
    print("=" * 50)
    print("🌐 Frontend: http://localhost:3000")
    print("🔌 Backend API: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    print("💡 Tips:")
    print("   • Enter your GPT-4o API key in the control panel")
    print("   • Configure MCTS and Evolution parameters")
    print("   • Click 'Start Evolution' to begin")
    print("   • Watch the real-time visualization!")
    print("=" * 50)
    print("🛑 Press Ctrl+C to stop both servers")
    
    def signal_handler(sig, frame):
        print("\n\n🛑 Shutting down EvolDSL...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for processes to terminate
        backend_process.wait()
        frontend_process.wait()
        
        print("✅ All services stopped. Goodbye!")
        sys.exit(0)
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Keep the script running and monitor processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process died unexpectedly")
                break
                
            if frontend_process.poll() is not None:
                print("❌ Frontend process died unexpectedly")
                break
    
    except KeyboardInterrupt:
        pass  # Handled by signal handler
    
    finally:
        # Cleanup
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()
        if frontend_process and frontend_process.poll() is None:
            frontend_process.terminate()

if __name__ == "__main__":
    main()