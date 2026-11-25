"""
Sistema de modulación en amplitud (AM) con análisis de ruido,
distorsión y atenuación.

Autor: Librado
Uso:   python modulacion_am.py
"""

import numpy as np                                   # Matemáticas con arreglos
import matplotlib.pyplot as plt                      # Gráficas
from scipy.signal import hilbert, butter, filtfilt   # Envolvente y filtro

# =====================================================================
# 1. DEFINICIÓN DE PARÁMETROS Y SEÑAL DE ENTRADA
# =====================================================================
fs = 100_000     # Frecuencia de muestreo (muestras por segundo)
T = 0.01         # Duración de la señal en segundos (10 ms)
fm = 500         # Frecuencia del mensaje (Hz)
fc = 10_000      # Frecuencia de la portadora (Hz)
mu = 0.5         # Índice de modulación (0.5 = modulación normal)

# Vector de tiempo: de 0 a T, con un punto cada 1/fs segundos
t = np.arange(0, T, 1 / fs)

# Señal mensaje: senoide de baja frecuencia con amplitud 1
mensaje = np.cos(2 * np.pi * fm * t)

# Portadora: senoide de alta frecuencia con amplitud 1
portadora = np.cos(2 * np.pi * fc * t)

# =====================================================================
# 2. IMPLEMENTACIÓN DE LA MODULACIÓN AM
#    s(t) = [1 + mu * m(t)] * portadora
# =====================================================================
senal_am = (1 + mu * mensaje) * portadora


# =====================================================================
# 3. FUNCIONES AUXILIARES
# =====================================================================
def espectro(x, fs):
    """Calcula el espectro de frecuencia (FFT) de una señal."""
    N = len(x)
    ventana = np.hanning(N)                      # Suaviza los bordes
    X = np.fft.rfft(x * ventana)                 # Transformada de Fourier
    f = np.fft.rfftfreq(N, 1 / fs)               # Eje de frecuencias (Hz)
    magnitud = 2 * np.abs(X) / np.sum(ventana)   # Amplitud de cada frecuencia
    return f, magnitud


def agregar_ruido(x, snr_db):
    """Suma ruido gaussiano a la señal según un SNR deseado (en dB)."""
    potencia_senal = np.mean(x ** 2)
    potencia_ruido = potencia_senal / (10 ** (snr_db / 10))
    ruido = np.random.normal(0, np.sqrt(potencia_ruido), len(x))
    return x + ruido


def pasa_bajas(x, f_corte, fs, orden=4):
    """Filtro pasa-bajas Butterworth: deja pasar solo frecuencias bajas."""
    b, a = butter(orden, f_corte / (fs / 2))
    return filtfilt(b, a, x)


def demodular(x):
    """Detector de envolvente: recupera el mensaje de la señal AM."""
    envolvente = np.abs(hilbert(x))                  # Contorno de la señal
    envolvente = envolvente - np.mean(envolvente)    # Quita componente constante
    return pasa_bajas(envolvente, 2 * fm, fs)        # Filtra residuos


# =====================================================================
# 4. VISUALIZACIÓN: MENSAJE ANTES DE MODULAR
# =====================================================================
plt.figure(figsize=(10, 3))
plt.plot(t * 1000, mensaje)                      # t en milisegundos
plt.title("Señal mensaje (antes de modular)")
plt.xlabel("Tiempo (ms)")
plt.ylabel("Amplitud")
plt.grid(True)
plt.tight_layout()
plt.savefig("01_mensaje.png", dpi=150)
plt.show()

# =====================================================================
# 5. VISUALIZACIÓN: SEÑAL AM EN TIEMPO Y FRECUENCIA
# =====================================================================
fig, ejes = plt.subplots(2, 1, figsize=(10, 6))

# --- Dominio del tiempo ---
ejes[0].plot(t * 1000, senal_am, label="Señal AM")
ejes[0].plot(t * 1000, 1 + mu * mensaje, "r--", label="Envolvente")
ejes[0].plot(t * 1000, -(1 + mu * mensaje), "r--")
ejes[0].set_title("Señal AM en el dominio del tiempo")
ejes[0].set_xlabel("Tiempo (ms)")
ejes[0].set_ylabel("Amplitud")
ejes[0].legend()
ejes[0].grid(True)

# --- Dominio de la frecuencia ---
f, mag = espectro(senal_am, fs)
ejes[1].plot(f / 1000, mag)
ejes[1].set_xlim(0, 20)                          # Mostramos hasta 20 kHz
ejes[1].set_title("Espectro de la señal AM (picos en fc-fm, fc y fc+fm)")
ejes[1].set_xlabel("Frecuencia (kHz)")
ejes[1].set_ylabel("Magnitud")
ejes[1].grid(True)

plt.tight_layout()
plt.savefig("02_am_tiempo_frecuencia.png", dpi=150)
plt.show()

# =====================================================================
# 6. ANÁLISIS DE RUIDO, DISTORSIÓN Y ATENUACIÓN
# =====================================================================
np.random.seed(42)   # Mismos resultados en cada ejecución

# Escenario A: canal ideal
rx_ideal = senal_am

# Escenario B: ruido moderado (20 dB) y fuerte (5 dB)
rx_ruido_20 = agregar_ruido(senal_am, 20)
rx_ruido_5 = agregar_ruido(senal_am, 5)

# Escenario C: distorsión por saturación (el amplificador recorta picos)
rx_distorsion = np.clip(senal_am * 1.5, -1.0, 1.0)

# Escenario D: atenuación fuerte (llega al 10 %) con ruido fijo del canal
sigma_ruido = 0.05
rx_atenuada = 0.1 * senal_am + np.random.normal(0, sigma_ruido, len(t))

# Escenario E: sobremodulación (mu = 1.5)
senal_sobre = (1 + 1.5 * mensaje) * portadora

escenarios = {
    "A) Canal ideal": rx_ideal,
    "B1) Ruido SNR = 20 dB": rx_ruido_20,
    "B2) Ruido SNR = 5 dB": rx_ruido_5,
    "C) Distorsión (saturación)": rx_distorsion,
    "D) Atenuación 10 % + ruido": rx_atenuada,
    "E) Sobremodulación (mu = 1.5)": senal_sobre,
}

fig, ejes = plt.subplots(len(escenarios), 3, figsize=(15, 3 * len(escenarios)))

print(f"{'Escenario':35s} Correlación con el mensaje")
for i, (nombre, rx) in enumerate(escenarios.items()):
    recuperado = demodular(rx)
    # Correlación: 1.0 = idéntico al mensaje, cerca de 0 = no se parecen
    correlacion = np.corrcoef(mensaje, recuperado)[0, 1]
    print(f"{nombre:35s} {correlacion:.3f}")

    # Columna 1: señal recibida en el tiempo
    ejes[i, 0].plot(t * 1000, rx)
    ejes[i, 0].set_title(f"{nombre} - señal recibida")
    ejes[i, 0].set_xlabel("Tiempo (ms)")

    # Columna 2: espectro de la señal recibida
    f, mag = espectro(rx, fs)
    ejes[i, 1].plot(f / 1000, mag)
    ejes[i, 1].set_xlim(0, 20)
    ejes[i, 1].set_title("Espectro")
    ejes[i, 1].set_xlabel("Frecuencia (kHz)")

    # Columna 3: mensaje original vs. recuperado (normalizado para comparar)
    ejes[i, 2].plot(t * 1000, mensaje, label="Original")
    ejes[i, 2].plot(t * 1000, recuperado / np.max(np.abs(recuperado)),
                    "--", label="Recuperado (normalizado)")
    ejes[i, 2].set_title(f"Mensaje recuperado (corr = {correlacion:.2f})")
    ejes[i, 2].set_xlabel("Tiempo (ms)")
    ejes[i, 2].legend()

plt.tight_layout()
plt.savefig("03_escenarios.png", dpi=120)
plt.show()
