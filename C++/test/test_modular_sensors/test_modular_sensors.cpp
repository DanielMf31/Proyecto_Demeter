#include <unity.h>
#include <vector>
#include <cstring>
#include <iostream>

#include "core/Node_Sensor.h"
#include "core/ProtocolEngine.h"
#include "hardware/sensors/DHTSensor.h"
#include "hardware/sensors/DS18B20Sensor.h"
#include "hardware/sensors/SoilMoistureSensor.h"
#include "communications/IComms.h"
#include "../mocks/MockComms.h"

// ==========================================
// MOCK COMMS STRATEGY
// ==========================================
// Moved to ../mocks/MockComms.h

// ==========================================
// UNIT TESTS: SENSORS
// ==========================================

void test_dht_sensor_mock() {
    // 1. Setup
    Demeter::Sensors::DHTSensor dht(4, 22, true); // Pin 4, Type 22, Mock=True
    
    // 2. Init
    TEST_ASSERT_TRUE(dht.init());
    TEST_ASSERT_EQUAL_STRING("DHT (Mock)", dht.getName().c_str());

    // 3. Read
    Demeter::SensorReading data;
    bool success = dht.read(data);

    // 4. Assert
    TEST_ASSERT_TRUE(success);
    TEST_ASSERT_TRUE(data.isValid);
    // Temp should be around 25 +/- 2
    TEST_ASSERT_FLOAT_WITHIN(3.0f, 25.0f, data.value1);
    // Hum should be around 50 +/- 5
    TEST_ASSERT_FLOAT_WITHIN(6.0f, 50.0f, data.value2);
}

void test_ds18b20_sensor_mock() {
    Demeter::Sensors::DS18B20Sensor temp(5, true); // Pin 5, Mock=True

    TEST_ASSERT_TRUE(temp.init());
    TEST_ASSERT_EQUAL_STRING("DS18B20 (Mock)", temp.getName().c_str());

    Demeter::SensorReading data;
    bool success = temp.read(data);

    TEST_ASSERT_TRUE(success);
    TEST_ASSERT_TRUE(data.isValid);
    // Temp should be 18-22
    TEST_ASSERT_FLOAT_WITHIN(3.0f, 20.0f, data.value1);
    TEST_ASSERT_EQUAL_FLOAT(0.0f, data.value2); // Humidity 0
}

void test_soil_sensor_mock() {
    Demeter::Sensors::SoilMoistureSensor soil(34, 3000, 1000, true);

    TEST_ASSERT_TRUE(soil.init());
    
    Demeter::SensorReading data;
    bool success = soil.read(data);

    TEST_ASSERT_TRUE(success);
    TEST_ASSERT_TRUE(data.isValid);
    // Value 0-100
    TEST_ASSERT_GREATER_OR_EQUAL(0.0f, data.value1);
    TEST_ASSERT_LESS_OR_EQUAL(100.0f, data.value1);
}

// ==========================================
// INTEGRATION TESTS: NODE -> PROTOCOL
// ==========================================

void test_node_integration() {
    // 1. Setup Mock System
    MockComms mockComms;
    ProtocolEngine engine(&mockComms);
    Node_Sensor node(2, &engine); // Node ID 2, using Node_Sensor

    // 2. Setup Sensor
    Demeter::Sensors::DHTSensor dht(4, 22, true);
    node.getSensorManager()->addSensor(&dht);

    // 3. Init
    node.begin();

    // 4. Trigger Update (Simulate Reporting Interval)
    node.setReportingConfig(1000, false); // 1 sec interval
    
    // Manual Engine Check
    float testTemp = 25.5;
    float testHum = 60.2;
    uint8_t target = 1; // Gateway
    
    engine.sendTempHumReport(target, testTemp, testHum);
    
    TEST_ASSERT_TRUE(mockComms.sendCalled);
    TEST_ASSERT_NOT_EMPTY(mockComms.lastSentData);
    
    // Verify Frame Content (Protocol V2)
    std::vector<uint8_t>& frame = mockComms.lastSentData;
    TEST_ASSERT_EQUAL_HEX8(0xFE, frame[0]); // SYNC
    
    // Check Payload (Offset 6)
    int16_t t_expected = (int16_t)(testTemp * 100);
    int16_t h_expected = (int16_t)(testHum * 100);
    
    uint8_t* payload = &frame[6];
    int16_t t_actual = payload[0] | (payload[1] << 8);
    int16_t h_actual = payload[2] | (payload[3] << 8);
    
    TEST_ASSERT_EQUAL_INT16(t_expected, t_actual);
    TEST_ASSERT_EQUAL_INT16(h_expected, h_actual);
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_dht_sensor_mock);
    RUN_TEST(test_ds18b20_sensor_mock);
    RUN_TEST(test_soil_sensor_mock);
    RUN_TEST(test_node_integration);
    UNITY_END();
    return 0;
}
