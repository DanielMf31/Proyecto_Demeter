import sys
from proyecto_demeter.config.settings import Settings

def main():
    print("--> Iniciando Proyecto_Demeter...")
    
    try:
        # Cargar configuración (valida .env y defaults)
        settings = Settings()
        
        print(f"--> Configuración cargada correctamente.")
        print(f"    App Name: {settings.app_name}")
        print(f"    Debug Mode: {settings.debug}")
        print(f"    LLM Provider: {settings.llm.provider} (Model: {settings.llm.model})")
        print(f"    Log Level: {settings.log_level}")
        
        # Aquí iría la lógica de arranque del servidor o proceso
        # if settings.use_raspberry_pi: ...
        
    except Exception as e:
        print(f"!!! Error crítico al iniciar: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
