/*
* DESCUBRIMIENTOS:
* - Hay que elaborar tests para probar las funciones principales
*
* DECISIONES TOMADAS:
* - Terminar de desarrollar las funciones y desarrollar tests.
*
* PENDIENTES:
* - Terminar desarrollo de funciones
* - Terminar unit tests principales
* - IMPORTANTE: Declarar instancias globales de constructores de cada clase
* -- Solucionar problema de referencias en Maquina de Estado respecto a EjecucionComandos
* -- Solución planteada. Variables de arrays de comandos deben pertenecer a EjecucionComandos.
*
* DECISIONES ARQUITECTURA:
* - Variables de datos sólo en class ProcesamientoDatos
* - EjecucionComandos sólo cambia estado de pines
* - MaquinaEstados controla la lógica de negocios únicamente
* - Configuracion declara los tipos de variables de datos, pero no los implementa
*
*
*
*
*
*/