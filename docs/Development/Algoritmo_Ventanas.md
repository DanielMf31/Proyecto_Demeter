# Algoritmo de Control de Ventilación Natural (PID + Termodinámica)

Este documento detalla la lógica matemática, física y de software empleada en el "Cerebro Central" (Controlador) para la apertura y cierre de las ventanas del invernadero. El sistema está diseñado en Python bajo una arquitectura Orientada a Objetos (POO), priorizando la estabilidad mecánica y la seguridad por encima de la velocidad de reacción.

---

## 1. Filtro Paso Bajo (Moving Average)

### El Problema del *Chattering*
Los sensores de bajo coste suelen presentar un alto nivel de ruido eléctrico o lecturas irregulares causadas por ráfagas de viento colándose por la ventana. Si el controlador reaccionara a los valores instantáneos, ordenaría abrir y cerrar las ventanas continuamente, provocando el desgaste prematuro de los motores mecánicos y relés (efecto conocido como *chattering*).

### La Solución Matemática
Se emplea un filtro paso bajo implementado como una **Media Móvil Simple (SMA - Simple Moving Average)**. La variable de proceso (PV) que ingresa al controlador no es el valor de la lectura actual ($x_t$), sino la media de las últimas $N$ lecturas (ventana).

$$ PV_t = \frac{1}{N} \sum_{i=0}^{N-1} x_{t-i} $$

En nuestro sistema, $N = 5$. Si el lazo de control corre a 1 Hz, la decisión de abrir la ventana siempre se basa en el promedio de los últimos 5 segundos, absorbiendo así los picos espurios.

---

## 2. Enclavamientos de Seguridad (Safety Interlocks)

Antes de realizar cualquier cálculo complejo o termodinámico, el orquestador (`GreenhouseController`) evalúa las reglas de seguridad física:

1. **Lluvia:** Un sensor de lluvia (Booleano) indica precipitación.
2. **Viento Extremo:** Un anemómetro registra ráfagas superiores a 40 km/h.

Si cualquiera de estas dos condiciones se cumple, el sistema **fuerza el cierre inmediato al 0%**. Esta capa evita que la planta se inunde, se enfríe de golpe o que las ventanas plásticas se rasguen por esfuerzo eólico. 

El código subyacente para esto tiene prioridad sobre el controlador PID y corta la ejecución de las fases posteriores devolviendo un *return* temprano.

---

## 3. Termodinámica y Viabilidad (Entalpía)

El objetivo de ventilar un invernadero en verano es evacuar energía. Si el aire exterior tiene mayor energía térmica que el aire interior, ventilar empeorará la situación térmica de las plantas.

### Cálculo de Entalpía ($h$)
La energía del aire no depende solo de la temperatura (calor sensible), sino también de la cantidad de vapor de agua que alberga (calor latente). La formula para evaluar esto proviene de las directrices de ASHRAE.

1.  **Presión de Saturación ($e_s$, ecuación de Magnus):**
    $$e_s = 0.6108 \cdot e^{\frac{17.27 \cdot T}{T + 237.3}}$$
2.  **Humedad Específica ($r$):** Relación de masa entre el vapor de agua y el aire seco (depende de la presión atmosférica $P$).
    $$r = \frac{0.622 \cdot (e_s \cdot \frac{HR}{100})}{P - (e_s \cdot \frac{HR}{100})}$$
3.  **Entalpía Especifica ($h$, en kJ/kg):**
    $$h = 1.006 \cdot T + r \cdot (2501 + 1.86 \cdot T)$$

### Decisión del Límite de Apertura
El orquestador calcula $h_{int}$ y $h_{ext}$. Si se da que $h_{ext} > h_{int}$, el sistema deduce que abrir completamente aumentará el estrés calórico de la planta. Por ende, **clampa el límite del PID** de forma dinámica y restringe la apertura a un máximo absoluto del 10% (necesario únicamente para renovación residual de CO2).

---

## 4. Controlador PID en Tiempo Discreto

En el corazón del sistema, un controlador *Proporcional-Integral-Derivativo* calcula el porcentaje de apertura ($u_t$) basándose en el Error de la temperatura objetivo ($SP$) frente a la temperatura medida ($PV$).

$$ Error (e_t) = SP - PV_t $$

> *Nota de ingeniería: Dado que abrir la ventana reduce la temperatura, la ganancia Proporcional ($K_p$) debe ser negativa.*

### Componentes de Control

1. **Término Proporcional ($P$):** Acción inmediata ante el error actual. 
    *   $P_t = K_p \cdot e_t$
2. **Término Integral ($I$):** Sumatoria de los errores pasados. Se encarga de atacar el error en estado estacionario (offset). Calculado mediante integración de Euler.
    *   $I_t = I_{t-1} + K_i \cdot e_t \cdot \Delta t$
3. **Término Derivativo ($D$):** Estudia la tendencia o velocidad del error. Si la temperatura ya está bajando rápido por sí sola, el término D frena al PID antes de que llegue a la meta para evitar pasarse de frenada (Overshoot).
    *   $D_t = K_d \cdot \frac{e_t - e_{t-1}}{\Delta t}$

### El Problema del *Windup*
Imaginemos que afuera hace 40°C. La ventana se abre al 100%, pero la temperatura interior no logra llegar al Setpoint de 24°C, quedándose estancada en 32°C. El error ($e_t = -8$) sigue existiendo ciclo tras ciclo. 

Si no hiciéramos nada, el Término Integral ($I_t$) comenzaría a acumular este error durante horas hasta llegar a una cifra matemática absurda (ej. +500%). Cuando finalmente por la noche la temperatura cayera a 20°C, la ventana se quedaría trabada al 100% hasta que ese valor acumulado restase todo lo almacenado temporalmente.

### Solución: Clampeo Anti-Windup
El método implementado revisa la salida teórica del controlador. Si $u_t > 100\%$, el integrador deshace su último paso ($I_t = I_t - K_i \cdot e_t \cdot \Delta t$) evitando que almacene inercia artificial mientras el motor ya no puede dar más de sí.

---

## 5. Feed-Forward Térmico

El PID reacciona al error. Es decir, primero dentro tiene que hacer calor para que ordene abrir la ventana. 
El **Feed-Forward** es una técnica anticipativa. Si el piranómetro exterior detecta más de $600 \, \text{W/m}^2$ de radiación solar, sabemos fehacientemente que la temperatura del invernadero subirá en cadena en diez o veinte minutos por el efecto invernadero masivo de los plásticos. 

Por tanto, introducimos un salto (ej. $+15\%$) al cálculo final del PID para abrir la apertura mecánicamente incluso cuando la temperatura interior se halle bajo el Setpoint, anticipándonos al calentón.

---

## 6. Banda Muerta (Deadband)

Para proteger al relé de conmutación del motor, se añade un control en el peldaño final. Si la ventana está al `30.0%` y el PID devuelve una demanda de `34.1%`, la diferencia es `4.1%`. 

Consideramos que el ruido y la pequeña ganancia térmica no ameritan la fatiga de arrancar el motor eléctrico de continua. Se requiere definir un parámetro estricto, por ejemplo, `DEADBAND = 10%`. Hasta que el PID no emita un valor $\ge 40\%$, o $\le 20\%$, la orden no se pasa el motor y todo permanece silenciado en el *backend*.
