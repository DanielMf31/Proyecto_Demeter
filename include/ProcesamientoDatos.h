#ifndef PROCESAMIENTODATOS_H
#define PROCESAMIENTODATOS_H

#include <Arduino.h>

class ProcesamientoDatos{
  private:
    // Variables internas que solo esta clase necesita
    int valores[4];  // Buffer temporal para procesar
    int comandoCount; // Contador interno de comandos
    
  public:
    // Constructor
    ProcesamientoDatos() {
      comandoCount = 0;
    }
    
    void LeerMensajesUART(int destino[100][4]) {
      while (Serial2.available() > 0) {
        String mensaje = Serial2.readStringUntil('\n');
        mensaje.trim();
        
        Serial.print("Recibido: ");
        Serial.println(mensaje);
        
        // Llamar a procesarMensaje con el array destino
        procesarMensaje(mensaje, destino);
      }
    }

  private:  
    void procesarMensaje(String mensajeRecibido, int destino[100][4]) {
      int start = 0;
      int index = 0;
      
      // Reiniciar valores array
      for(int i = 0; i < 4; i++) {
        valores[i] = 0;
      }
      
      // Recorrer cada carácter del mensaje
      for (int i = 0; i <= mensajeRecibido.length(); i++) {
        // Si encontramos un espacio O llegamos al final
        if (mensajeRecibido[i] == ' ' || i == mensajeRecibido.length()) {
          String numeroStr = mensajeRecibido.substring(start, i);
          valores[index] = numeroStr.toInt();
          start = i + 1;
          index++;
          
          // Si ya tenemos 4 números, salir
          if (index >= 4) break;
        }
      }
      
      // Guardar en el array destino SOLO UNA VEZ
      for(int j = 0; j < 4; j++) {
        destino[comandoCount][j] = valores[j];
      }
      
      comandoCount++;
      
      // Protección para no exceder el tamaño del array
      if (comandoCount >= 100) {
        comandoCount = 0; // Resetear o manejar overflow
      }
    }
};

#endif