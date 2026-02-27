Vectorización de operaciones

Cuando quieres realizar una operación o varias a un dataframe de Python existe la posibilidad de vectoriza la información de forma que a la función que nos calcula esas variables la pasamos entero el vector mediante pandas y numpy y eso permite usar un modo de la CPU llamada SIMD (Single Instruction, Multiple Data) que permite realizar la misma operación a varios datos a la vez. Esto hace que el cálculo sea mucho más rápido que si lo hiciéramos con un bucle for. Por lo tanto, siempre que podamos debemos vectorizar las operaciones.

