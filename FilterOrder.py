import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, freqz

# Frequência de corte e taxa de amostragem
cutoff = 1  # Frequência de corte normalizada (em relação à Nyquist)
fs = 10  # Taxa de amostragem fictícia
nyquist = 0.5 * fs  # Frequência de Nyquist
cutoff_normalized = cutoff / nyquist  # Freq. de corte normalizada

# Ordens do filtro
orders = [1, 2, 3, 4,6, 7, 10]

# Plotando as respostas em frequência
plt.figure(figsize=(10, 6))

for order in orders:
    b, a = butter(order, cutoff_normalized, btype='low', analog=False)  # Filtro passa-baixa
    w, h = freqz(b, a, worN=8000)  # Calculando resposta em frequência
    plt.plot(w / np.pi * nyquist, np.abs(h), label=f"{order}ª ordem")  # Normalizado para Hz

# Configuração do gráfico
plt.title("Resposta em Frequência para Diferentes Ordens do Filtro Butterworth")
plt.xlabel("Frequência (Hz)")
plt.ylabel("Ganho")
plt.grid()
plt.legend()
plt.show()
