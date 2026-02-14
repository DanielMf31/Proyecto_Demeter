#include "core/SystemContext.h"

namespace Demeter {

    SystemContext::SystemContext() 
        : _nodeId(0), _gatewayId(1), _role(NodeRole::SENSOR),
          _currentState(SystemState::BOOT), _batteryMv(0), _uptimeSeconds(0), _lastErrorCode(0),
          _deepSleepEnabled(false), _reportIntervalMs(0) {
    }

    void SystemContext::setIdentity(uint8_t id, NodeRole role, uint8_t gatewayId) {
        _nodeId = id;
        _role = role;
        _gatewayId = gatewayId;
    }

    void SystemContext::setState(SystemState state) {
        _currentState = state;
    }

    void SystemContext::updateBattery(uint16_t mv) {
        _batteryMv = mv;
    }

    void SystemContext::setConfig(uint32_t intervalMs, bool deepSleep) {
        _reportIntervalMs = intervalMs;
        _deepSleepEnabled = deepSleep;
    }

}
