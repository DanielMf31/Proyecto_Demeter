/**
 * @file Node_Gateway.cpp
 * @brief Implementación de la Lógica del Nodo Concentrador.
 * 
 * ============================================================================
 * DECISIONES DE ARQUITECTURA Y DISEÑO
 * ============================================================================
 * ¿Por qué esta clase separada y no un único main.cpp gigante?
 * 1. **Principio de Responsabilidad Única (SRP):** El Gateway tiene un rol
 *    muy específico: unir dos redes diferentes (ej. ESP-NOW y UART) manteniendo
 *    un estado lógico. `main_gateway.cpp` sólo debe ocuparse del "setup de Arduino",
 *    mientras que esta clase se ocupa de la "lógica de negocio abstracta" del nodo.
 * 2. **Composición sobre Herencia:** Un Gateway, en Demeter, es un híbrido. Puede
 *    tener actuadores locales (botones) y sensores, además de enrutar. Por esto
 *    se instancian internamente `GpioController` y `SensorManager`.
 */
#include "core/Node_Gateway.h"
#include <Arduino.h>

/**
 * @brief Constructor del Nodo Gateway.
 * ¿Por qué inicializamos los punteros a nulo y pasamos el ProtocolEngine?
 * Porque el ProtocolEngine es una dependencia inyectada (IoC - Inversión de Control).
 * Esto nos permite mockear el motor en pruebas unitarias o cambiar el protocolo
 * sin alterar la lógica del nodo. Las responsabilidades de hardware interno
 * (Executor y SensorManager) nacen y mueren con el Gateway, por ello se hace `new` aquí.
 */
Node_Gateway::Node_Gateway(uint8_t id, ProtocolEngine* engine) 
    : _nodeId(id), _engine(engine), _systemManager(nullptr) {
    
    // Instanciación de capacidades híbridas.
    _executor = new GpioController();
    _sensorManager = new SensorManager();

    // ¿Por qué el SystemManager se crea aquí dentro si inyectamos Engine?
    // Porque es el "cerebro" orquestador exclusivo de este ciclo de vida de nodo.
    // Además, hay que vincularle explícitamente los managers de hardware locales.
    if (_engine) {
        _systemManager = new SystemManager(_engine);
        _systemManager->enableExecutor(_executor);
        _systemManager->enableSensorManager(_sensorManager);
    }
}

Node_Gateway::~Node_Gateway() {
    delete _executor;
    delete _sensorManager;
    if (_systemManager) {
        delete _systemManager;
    }
}

/**
 * @brief Inicializa los descriptores lógicos y de hardware de la pasarela.
 * 
 * ¿Por qué no hacer esto en el constructor?
 * Hardware vs Software. En C++ embebido es una *muy mala práctica* invocar
 * rutinas de hardware (como pinMode) en un constructor global, porque el bootloader
 * y el RTOS de la placa aún no han completado su inicialización subyacente.
 * Se divide rígidamente en `constructor` (memoria/objetos) y `begin()` (hardware).
 */
void Node_Gateway::begin() {
    if (!_systemManager) return;

    // 1. Initialize Context - Define la identidad para los paquetes.
    auto& ctx = _systemManager->getContext();
    ctx.setIdentity(_nodeId, Demeter::NodeRole::GATEWAY);

    // 2. Initialize Hardware Config
    if (auto* executor = _systemManager->getExecutor()) {
        // En una hipotética placa Gateway física, los pines 4 al 7 
        // podrían ser botones para interactuar sin conectividad.
        executor->setPins({4, 5, 6, 7}); 
    }

    // 3. Initialize System Logic
    _systemManager->setup(); // Levanta callbacks y configuraciones base.
}

/**
 * @brief Tick concurrente enfocado a procesar tramas de las dos estrategias.
 * 
 * ¿Por qué delegamos a un método update() en vez de usar interrupciones (ISRs)?
 * Evitar "Race Conditions" y bloqueos de RTOS. Ciertas librerías no toleran llamadas
 * desde el contexto de interrupción de hardware (ej. `Serial.print` o `esp_now_send`).
 * Patrón "Polling / Super-loop": Los buffers temporales se llenan en background asíncrono,
 * y aquí, de forma limpia, determinista y "Thread-Safe", procesamos paquetes.
 */
void Node_Gateway::update() {
    // Transfiere cpu cycle al orquestador central que parseará el puerto.
    if (_systemManager) {
        _systemManager->update();
    } else if (_engine) {
        // Fallback si no hay system manager completo.
        _engine->update();
    }
}
