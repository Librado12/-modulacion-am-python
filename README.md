# Modulación en Amplitud (AM) con Python

## Descripción
Implementación de un sistema de modulación en amplitud (AM) y análisis de su
desempeño bajo ruido, distorsión y atenuación, en el dominio del tiempo y de la
frecuencia.

## Requisitos
- Python 3.9 o superior
- Librerías: NumPy, SciPy, Matplotlib

## Instalación y uso
```bash
pip install -r requirements.txt
python modulacion_am.py
```
El script muestra las gráficas, las guarda como imágenes `.png` y imprime en
consola una tabla con la correlación entre el mensaje original y el recuperado.

## Qué hace el código
1. Genera un mensaje de 500 Hz y una portadora de 10 kHz.
2. Modula en amplitud con índice de modulación `mu = 0.5`:
   `s(t) = [1 + mu * m(t)] * cos(2π fc t)`.
3. Grafica la señal en el tiempo y su espectro (picos en 9.5, 10 y 10.5 kHz).
4. Simula seis escenarios de canal: ideal, ruido (20 dB y 5 dB), distorsión por
   saturación, atenuación con ruido y sobremodulación.
5. Demodula con detector de envolvente (transformada de Hilbert + filtro
   pasa-bajas) y mide la calidad con el coeficiente de correlación.

## Resultados

### Mensaje original
![Mensaje](01_mensaje.png)

### Señal AM: tiempo y frecuencia
![AM](02_am_tiempo_frecuencia.png)

### Escenarios de canal
![Escenarios](03_escenarios.png)

| Escenario | Correlación con el mensaje |
|---|---|
| A) Canal ideal | 0.997 |
| B1) Ruido SNR = 20 dB | 0.996 |
| B2) Ruido SNR = 5 dB | 0.961 |
| C) Distorsión (saturación) | 0.960 |
| D) Atenuación 10 % + ruido | 0.955 |
| E) Sobremodulación (mu = 1.5) | 0.989 |

> La correlación es una métrica gruesa: el filtro pasa-bajas del receptor
> elimina gran parte del ruido, por lo que los valores se mantienen altos. Las
> diferencias entre escenarios se aprecian mejor en las gráficas (piso de ruido
> en el espectro, armónicos por saturación, envolvente deformada).

## Conclusiones
- AM transmite información variando la amplitud de la portadora; su espectro
  tiene portadora y dos bandas laterales (ancho de banda = 2·fm).
- El ruido eleva el piso de ruido del espectro y reduce el SNR.
- La distorsión por saturación crea armónicos que no existían en la señal.
- La atenuación debilita la señal frente a un ruido de canal constante, lo que
  reduce el SNR efectivo.
- Con mu > 1 la envolvente deja de copiar al mensaje (sobremodulación).

## Autor
Librado - Ingeniería en Desarrollo de Software
