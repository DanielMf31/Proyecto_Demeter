import sys
import os
import subprocess
import argparse
import signal
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from proyecto_demeter.config import settings

# Setup Logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DemeterGUI")

def main():
    """
    Launcher for the Demeter Professional GUI.
    """
    parser = argparse.ArgumentParser(description="Demeter V2 Professional GUI")
    parser.add_argument("--host", default="127.0.0.1", help="Backend Host IP (default: 127.0.0.1)")
    parser.add_argument("--port", default=8888, type=int, help="Backend Socket Port (default: 8888)")
    
    args = parser.parse_args()
    
    # Configure Environment for ViewModel
    os.environ["DEMETER_HOST"] = args.host
    os.environ["DEMETER_SOCKET_PORT"] = str(args.port)

    print("🚀 Starting Demeter V2 Professional GUI...")
    print(f"📡 Connecting to Backend at: {args.host}:{args.port}")
    
    # Check if backend is likely running (optional)
    # Could check port 8888, but let's just launch
    
    # Import here to ensure sys.path is set
    try:
        # 1. Show Login Window
        from proyecto_demeter.ui.login_view import LoginWindow
        print("🔐 Launching Login Window...")
        login_app = LoginWindow()
        login_app.mainloop()
        
        if not login_app.authenticated:
            print("⛔ Authentication required. Exiting.")
            sys.exit(0)
            
        print("✅ Authentication Successful. Loading Main App...")

        # 2. Show Main App
        from proyecto_demeter.ui.gui_main_ctk import DemeterApp
        app = DemeterApp()
        
        # Determine protocol for closing
        def on_closure():
            app.on_closing()
            
        app.protocol("WM_DELETE_WINDOW", on_closure)
        app.mainloop()
        
    except ImportError as e:
        print(f"❌ Failed to import GUI components: {e}")
        print(f"   Ensure you are running from the Python/ directory.")
        sys.exit(1)
        
if __name__ == "__main__":
    main()
