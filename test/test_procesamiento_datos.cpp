#include <Arduino.h>
#include <unity.h>
#include "ProcesamientoDatos.h"

// ==================== TESTER CLASS ====================
class TestProcesamientoDatos {
public:
    // ✅ Gracias a friend class, podemos acceder a métodos privados
    static void testProcesarMensaje(ProcesamientoDatos& proc, String mensaje, int destino[100][4]) {
        proc.procesarMensaje(mensaje, destino);
    }
    
    static void testCargarComandos(ProcesamientoDatos& proc, int origen[10][4], Comando destino[10]) {
        proc.cargarComandos(origen, destino);
    }
};

// ==================== TESTS ====================
void test_constructor() {
    ProcesamientoDatos proc;
    
    TEST_ASSERT_EQUAL(0, proc.getComandoCount());
    TEST_ASSERT_EQUAL(0, proc.getComandoActual());
    TEST_ASSERT_EQUAL(2, proc.getNumeroComandos());  // Por los arrays de prueba
}

void test_procesar_mensaje_valido() {
    ProcesamientoDatos proc;
    int destino[100][4] = {0};
    
    // Given - When
    TestProcesamientoDatos::testProcesarMensaje(proc, "1 2 1 100", destino);
    
    // Then
    TEST_ASSERT_EQUAL(1, destino[0][0]);
    TEST_ASSERT_EQUAL(2, destino[0][1]);
    TEST_ASSERT_EQUAL(1, destino[0][2]);
    TEST_ASSERT_EQUAL(100, destino[0][3]);
    TEST_ASSERT_EQUAL(1, proc.getComandoCount());
}

void test_cargar_comandos() {
    ProcesamientoDatos proc;
    int origen[2][4] = {{1, 2, 1, 100}, {3, 4, 0, 50}};
    Comando destino[10];
    
    // Given - When
    TestProcesamientoDatos::testCargarComandos(proc, origen, destino);
    
    // Then
    TEST_ASSERT_EQUAL(1, destino[0].actuador);
    TEST_ASSERT_EQUAL(2, destino[0].numero);
    TEST_ASSERT_EQUAL(1, destino[0].estado);
    TEST_ASSERT_EQUAL(100, destino[0].duracion);
    TEST_ASSERT_FALSE(destino[0].activo);
}

void test_incrementar_comando_actual() {
    ProcesamientoDatos proc;
    int inicial = proc.getComandoActual();
    
    proc.incrementarComandoActual();
    
    TEST_ASSERT_EQUAL(inicial + 1, proc.getComandoActual());
}

// ==================== SETUP ====================
void setup() {
    delay(2000);
    UNITY_BEGIN();
    
    RUN_TEST(test_constructor);
    RUN_TEST(test_procesar_mensaje_valido);
    RUN_TEST(test_cargar_comandos);
    RUN_TEST(test_incrementar_comando_actual);
    
    UNITY_END();
}

void loop() {}