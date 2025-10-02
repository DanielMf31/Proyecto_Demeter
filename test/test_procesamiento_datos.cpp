#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unity.h>

// ==================== MOCKS EXPLICADOS PASO A PASO ====================

/**
 * MOCK DE STRING
 * ¿Por qué? Porque String es una clase de Arduino que no existe en PC
 * Creamos una versión simplificada con solo lo que necesitamos
 */
class String {
private:
    char* data;
    size_t str_length;

    // Helper para eliminar espacios
    void removeSpaces(char* str) {
        if (!str) return;
        
        char* i = str;
        char* j = str;
        while (*j != '\0') {
            if (*j != ' ' && *j != '\t' && *j != '\n' && *j != '\r') {
                *i = *j;
                i++;
            }
            j++;
        }
        *i = '\0';
    }

public:
    // Constructor por defecto
    String() : data(nullptr), str_length(0) {}
    
    // Constructor desde const char*
    String(const char* str) {
        if (str) {
            str_length = strlen(str);
            data = (char*)malloc(str_length + 1);
            strcpy(data, str);
        } else {
            data = nullptr;
            str_length = 0;
        }
    }
    
    // Constructor de copia
    String(const String& other) {
        if (other.data) {
            str_length = other.str_length;
            data = (char*)malloc(str_length + 1);
            strcpy(data, other.data);
        } else {
            data = nullptr;
            str_length = 0;
        }
    }
    
    // Destructor
    ~String() {
        free(data);
    }
    
    // Operador de asignación
    String& operator=(const String& other) {
        if (this != &other) {
            free(data);
            if (other.data) {
                str_length = other.str_length;
                data = (char*)malloc(str_length + 1);
                strcpy(data, other.data);
            } else {
                data = nullptr;
                str_length = 0;
            }
        }
        return *this;
    }
    
    /**
     * MOCK DE substring()
     * Extrae una parte del string entre start y end
     */
    String substring(int start, int end) const {
        // Validaciones
        if (!data || start < 0 || end > (int)str_length || start >= end) {
            return String();  // String vacío
        }
        
        int subLength = end - start;
        char* subData = (char*)malloc(subLength + 1);
        strncpy(subData, data + start, subLength);
        subData[subLength] = '\0';
        
        String result(subData);
        free(subData);
        return result;
    }
    
    /**
     * MOCK DE toInt()
     * Convierte string a número entero
     */
    int toInt() const {
        if (!data) return 0;
        return atoi(data);  // Usa la función estándar de C
    }
    
    /**
     * MOCK DE trim()
     * Elimina espacios al inicio y final
     */
    void trim() {
        if (!data) return;
        
        // Trim izquierdo
        int start = 0;
        while (data[start] == ' ' || data[start] == '\t' || 
               data[start] == '\n' || data[start] == '\r') {
            start++;
        }
        
        // Trim derecho
        int end = str_length - 1;
        while (end >= start && (data[end] == ' ' || data[end] == '\t' || 
                                data[end] == '\n' || data[end] == '\r')) {
            end--;
        }
        
        if (start > 0 || end < (int)str_length - 1) {
            int newLength = end - start + 1;
            char* newData = (char*)malloc(newLength + 1);
            strncpy(newData, data + start, newLength);
            newData[newLength] = '\0';
            
            free(data);
            data = newData;
            str_length = newLength;
        }
    }
    
    // Longitud del string
    int length() const { 
        return (int)str_length; 
    }
    
    // Acceso a caracteres individuales
    char operator[](int index) const {
        if (index < 0 || index >= (int)str_length || !data) 
            return '\0';
        return data[index];
    }
    
    // Conversión a const char* (para printf)
    const char* c_str() const { 
        return data ? data : ""; 
    }
    
    // Para debugging
    void printDebug() const {
        printf("String['%s', length=%d]\n", data ? data : "NULL", (int)str_length);
    }
};

/**
 * MOCK DE SERIAL
 * Simula el puerto serie de Arduino
 */
class MockSerial {
private:
    int available_data;
    const char** test_messages;
    int current_message;
    int total_messages;

public:
    MockSerial() : available_data(0), test_messages(nullptr), 
                   current_message(0), total_messages(0) {}
    
    // Configurar mensajes de prueba
    void setTestMessages(const char* messages[], int count) {
        test_messages = messages;
        total_messages = count;
        current_message = 0;
        available_data = count > 0 ? 1 : 0;
    }
    
    void begin(unsigned long baudrate) {
        printf("[MockSerial] Iniciado con baudrate: %lu\n", baudrate);
    }
    
    int available() {
        return available_data;
    }
    
    String readStringUntil(char terminator) {
        if (current_message < total_messages && test_messages) {
            String result(test_messages[current_message]);
            current_message++;
            available_data = (current_message < total_messages) ? 1 : 0;
            printf("[MockSerial] Leyendo: '%s'\n", result.c_str());
            return result;
        }
        return String("");  // String vacío
    }
    
    size_t print(const char* str) {
        printf("%s", str);
        return strlen(str);
    }
    
    size_t println(const char* str) {
        printf("%s\n", str);
        return strlen(str);
    }
    
    size_t print(int value) {
        printf("%d", value);
        return 1;
    }
    
    size_t println(int value) {
        printf("%d\n", value);
        return 1;
    }
};

/**
 * MOCK DE millis()
 * Simula el tiempo transcurrido
 */
static unsigned long mock_millis = 0;
unsigned long millis() {
    mock_millis += 100;  // Incrementamos en 100ms cada vez que se llama
    return mock_millis;
}

/**
 * MOCK DE digitalWrite()
 * Simula escribir en un pin digital
 */
void digitalWrite(int pin, int value) {
    printf("[digitalWrite] Pin %d -> %s\n", pin, value ? "HIGH" : "LOW");
}

// Crear instancias globales de los mocks
MockSerial Serial;
MockSerial Serial2;

// ==================== TESTER CLASS ====================
class TestProcesamientoDatos {
public:
    /**
     * Gracias a friend class, podemos acceder a métodos privados
     * sin necesidad de hacerlos públicos
     */
    static void testProcesarMensaje(ProcesamientoDatos& proc, String mensaje, int destino[100][4]) {
        printf("[Tester] Ejecutando procesarMensaje...\n");
        proc.procesarMensaje(mensaje, destino);
    }
    
    static void testCargarComandos(ProcesamientoDatos& proc, int origen[10][4], Comando destino[10]) {
        printf("[Tester] Ejecutando cargarComandos...\n");
        proc.cargarComandos(origen, destino);
    }
};

// ==================== INCLUDES REALES ====================
#include "Configuracion.h"
#include "ProcesamientoDatos.h"

// ==================== TESTS COMPLETOS ====================

void test_constructor_inicializa_variables() {
    printf("\n🔧 TEST 1: Constructor inicializa variables\n");
    ProcesamientoDatos proc;
    
    TEST_ASSERT_EQUAL(0, proc.getComandoCount());
    TEST_ASSERT_EQUAL(0, proc.getComandoActual());
    TEST_ASSERT_EQUAL(2, proc.getNumeroComandos());  // Por el array de prueba
    
    printf("✅ Constructor funciona correctamente\n");
}

void test_procesar_mensaje_valido_4_numeros() {
    printf("\n🔧 TEST 2: Procesar mensaje válido con 4 números\n");
    ProcesamientoDatos proc;
    int destino[100][4] = {0};
    
    TestProcesamientoDatos::testProcesarMensaje(proc, "1 2 1 100", destino);
    
    TEST_ASSERT_EQUAL(1, destino[0][0]);
    TEST_ASSERT_EQUAL(2, destino[0][1]);
    TEST_ASSERT_EQUAL(1, destino[0][2]);
    TEST_ASSERT_EQUAL(100, destino[0][3]);
    TEST_ASSERT_EQUAL(1, proc.getComandoCount());
    
    printf("✅ Mensaje '1 2 1 100' procesado como [%d, %d, %d, %d]\n", 
           destino[0][0], destino[0][1], destino[0][2], destino[0][3]);
}

void test_procesar_mensaje_con_espacios_extras() {
    printf("\n🔧 TEST 3: Procesar mensaje con espacios extras\n");
    ProcesamientoDatos proc;
    int destino[100][4] = {0};
    
    TestProcesamientoDatos::testProcesarMensaje(proc, "   1   2   3   4   ", destino);
    
    TEST_ASSERT_EQUAL(1, destino[0][0]);
    TEST_ASSERT_EQUAL(2, destino[0][1]);
    TEST_ASSERT_EQUAL(3, destino[0][2]);
    TEST_ASSERT_EQUAL(4, destino[0][3]);
    
    printf("✅ Espacios extras manejados correctamente\n");
}

void test_procesar_mensaje_incompleto() {
    printf("\n🔧 TEST 4: Procesar mensaje incompleto (solo 2 números)\n");
    ProcesamientoDatos proc;
    int destino[100][4] = {0};
    
    TestProcesamientoDatos::testProcesarMensaje(proc, "5 6", destino);
    
    TEST_ASSERT_EQUAL(5, destino[0][0]);
    TEST_ASSERT_EQUAL(6, destino[0][1]);
    TEST_ASSERT_EQUAL(0, destino[0][2]);  // Debe rellenar con 0
    TEST_ASSERT_EQUAL(0, destino[0][3]);  // Debe rellenar con 0
    
    printf("✅ Mensaje incompleto rellenado con ceros\n");
}

void test_procesar_mensaje_con_letras() {
    printf("\n🔧 TEST 5: Procesar mensaje con caracteres no numéricos\n");
    ProcesamientoDatos proc;
    int destino[100][4] = {0};
    
    TestProcesamientoDatos::testProcesarMensaje(proc, "1 a 3 b", destino);
    
    TEST_ASSERT_EQUAL(1, destino[0][0]);
    TEST_ASSERT_EQUAL(0, destino[0][1]);  // 'a' se convierte a 0
    TEST_ASSERT_EQUAL(3, destino[0][2]);
    TEST_ASSERT_EQUAL(0, destino[0][3]);  // 'b' se convierte a 0
    
    printf("✅ Caracteres no numéricos convertidos a 0\n");
}

void test_cargar_comandos_desde_array() {
    printf("\n🔧 TEST 6: Cargar comandos desde array 2D a struct\n");
    ProcesamientoDatos proc;
    
    int origen[2][4] = {
        {1, 2, 1, 100},  // Comando 1: actuador=1, numero=2, estado=1, duracion=100
        {3, 4, 0, 50}    // Comando 2: actuador=3, numero=4, estado=0, duracion=50
    };
    
    Comando destino[10] = {};
    
    TestProcesamientoDatos::testCargarComandos(proc, origen, destino);
    
    // Verificar primer comando
    TEST_ASSERT_EQUAL(1, destino[0].actuador);
    TEST_ASSERT_EQUAL(2, destino[0].numero);
    TEST_ASSERT_EQUAL(1, destino[0].estado);
    TEST_ASSERT_EQUAL(100, destino[0].duracion);
    TEST_ASSERT_FALSE(destino[0].activo);  // Debe inicializar como falso
    TEST_ASSERT_EQUAL(0, destino[0].inicio);  // Tiempo inicial en 0
    
    // Verificar segundo comando
    TEST_ASSERT_EQUAL(3, destino[1].actuador);
    TEST_ASSERT_EQUAL(4, destino[1].numero);
    TEST_ASSERT_EQUAL(0, destino[1].estado);
    TEST_ASSERT_EQUAL(50, destino[1].duracion);
    
    printf("✅ Comandos cargados correctamente en estructura\n");
}

void test_incrementar_comando_actual() {
    printf("\n🔧 TEST 7: Incrementar comando actual\n");
    ProcesamientoDatos proc;
    
    int inicial = proc.getComandoActual();
    proc.incrementarComandoActual();
    
    TEST_ASSERT_EQUAL(inicial + 1, proc.getComandoActual());
    
    printf("✅ Comando actual incrementado de %d a %d\n", 
           inicial, proc.getComandoActual());
}

void test_lectura_uart_simulada() {
    printf("\n🔧 TEST 8: Simulación completa de lectura UART\n");
    ProcesamientoDatos proc;
    int destino[100][4] = {0};
    
    // Configurar mensajes de prueba en el mock de Serial
    const char* mensajes_prueba[] = {
        "1 2 1 100",
        "3 4 0 50", 
        "5 6 1 200"
    };
    
    Serial2.setTestMessages(mensajes_prueba, 3);
    
    // Ejecutar lectura UART
    proc.LeerMensajesUART(destino);
    
    // Verificar que se procesaron los 3 mensajes
    TEST_ASSERT_EQUAL(1, destino[0][0]);
    TEST_ASSERT_EQUAL(3, destino[1][0]);
    TEST_ASSERT_EQUAL(5, destino[2][0]);
    
    printf("✅ Lectura UART simulada procesó %d mensajes\n", proc.getComandoCount());
}

void test_getters_devuelven_referencias_validas() {
    printf("\n🔧 TEST 9: Getters devuelven referencias modificables\n");
    ProcesamientoDatos proc;
    
    Comando* comandos = proc.getComandosParsed();
    TEST_ASSERT_NOT_NULL(comandos);
    
    // Modificar a través del getter
    comandos[0].actuador = 999;
    comandos[0].estado = 1;
    
    // Verificar que los cambios se mantienen
    TEST_ASSERT_EQUAL(999, proc.getComandosParsed()[0].actuador);
    TEST_ASSERT_EQUAL(1, proc.getComandosParsed()[0].estado);
    
    printf("✅ Getters permiten modificación directa\n");
}

void test_overflow_proteccion() {
    printf("\n🔧 TEST 10: Protección contra overflow\n");
    ProcesamientoDatos proc;
    int destino[100][4] = {0};
    
    // Procesar muchos mensajes
    for (int i = 0; i < 150; i++) {
        TestProcesamientoDatos::testProcesarMensaje(proc, "1 2 3 4", destino);
    }
    
    // El contador no debe exceder 100
    TEST_ASSERT_LESS_OR_EQUAL(100, proc.getComandoCount());
    
    printf("✅ Protección contra overflow funciona (count=%d)\n", proc.getComandoCount());
}

// ==================== CONFIGURACIÓN TESTS ====================
int main() {
    printf("🚀 INICIANDO SUITE DE TESTS COMPLETA\n");
    printf("=====================================\n");
    
    // Resetear mock de tiempo
    mock_millis = 0;
    
    UNITY_BEGIN();
    
    RUN_TEST(test_constructor_inicializa_variables);
    RUN_TEST(test_procesar_mensaje_valido_4_numeros);
    RUN_TEST(test_procesar_mensaje_con_espacios_extras);
    RUN_TEST(test_procesar_mensaje_incompleto);
    RUN_TEST(test_procesar_mensaje_con_letras);
    RUN_TEST(test_cargar_comandos_desde_array);
    RUN_TEST(test_incrementar_comando_actual);
    RUN_TEST(test_lectura_uart_simulada);
    RUN_TEST(test_getters_devuelven_referencias_validas);
    RUN_TEST(test_overflow_proteccion);
    
    int test_result = UNITY_END();
    
    printf("\n=====================================\n");
    if (test_result == 0) {
        printf("🎉 TODOS LOS TESTS PASARON!\n");
    } else {
        printf("❌ ALGUNOS TESTS FALLARON\n");
    }
    
    return test_result;
}