
import tkinter as tk
from utils.logger import sys_logger
from src.gui_controller import DemeterGUI
import logging

def main():
    # 1. Inicializar Sistema de Logs
    sys_logger.setup()
    logger = logging.getLogger("Main")
    
    logger.info("Iniciando Aplicación Demeter...")

    # 2. Iniciar GUI
    try:
        root = tk.Tk()
        app = DemeterGUI(root)
        
        logger.info("GUI iniciada. Entrando en mainloop.")
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"Error fatal en la aplicación: {e}", exc_info=True)
    finally:
        logger.info("Aplicación cerrada.")

if __name__ == "__main__":
    main()
