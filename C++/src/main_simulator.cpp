/*
 * SIMULADOR NATIVO
 * Compilar con: pio run -e simulator
 * Uso: echo -ne "\xFE..." | ./.pio/build/simulator/program
 */

#ifdef NATIVE_ENV

#include <iostream>
#include <vector>
#include <unistd.h>
#include <fcntl.h>

#include "communications/IComms.h"
#include "core/ProtocolEngine.h"
#include "core/GpioController.h"
#include "core/SystemContext.h"
#include "core/InternalTypes.h"

#include <sys/ioctl.h>

// Strategy that reads from STDIN
class StdinStrategy : public IComms {
public:
    void begin() override {}

    void send(const uint8_t* data, size_t length) override {
        // Simulator Output (Response to Host) output to CER R to avoid mixing with GPIO logs if we wanted strict separation
        // But plan said stdout. Let's keep using stdout but maybe prefix.
        // Actually, Python script separates stdout/stderr.
        // Let's print TX to stderr so stdout is just GPIO logs?
        // Or just keep it as is, Python parses stdout.
    }

    bool available() override {
        int bytes = 0;
        if (ioctl(STDIN_FILENO, FIONREAD, &bytes) == 0) {
            return bytes > 0;
        }
        return false;
    }

    std::vector<uint8_t> read() override {
        std::vector<uint8_t> buffer;
        int bytes = 0;
        ioctl(STDIN_FILENO, FIONREAD, &bytes);
        if (bytes > 0) {
            buffer.resize(bytes);
            ::read(STDIN_FILENO, buffer.data(), bytes);
        }
        return buffer;
    }
};

StdinStrategy stdinStrat;
ProtocolEngine engine(&stdinStrat);
GpioController gpio;
SystemContext systemCtx(engine, gpio);

int main() {
    std::cerr << "=== DEMETER SIMULATOR STARTED ===" << std::endl;
    
    systemCtx.setup();
    
    // Inject a special Spy into GpioController logic? 
    // Ideally GpioController in Native Mode already prints to stdout.
    // Let's rely on GpioController.cpp's native implementation logs.

    while (true) {
        systemCtx.loop();
        
        // Preventing CPU Hog in infinite loop
        usleep(10000); // 10ms
        
        if (std::cin.eof()) break;
    }
    
    return 0;
}

#endif
