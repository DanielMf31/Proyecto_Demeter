import sys
import os
import subprocess

# Add src to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.append(SRC_DIR)

def main():
    """
    Launcher for the Demeter Professional GUI.
    """
    print("🚀 Starting Demeter V2 Professional GUI...")
    
    # Check if backend is likely running (optional)
    # Could check port 8888, but let's just launch
    
    # Import here to ensure sys.path is set
    try:
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
