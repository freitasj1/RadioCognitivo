import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import serial
import time
import tkinter as tk
import threading as th

# Configurações da porta serial
porta = "COM4"  
baudrate = 115200  
duracao = 2  
fs = 1000  
num_amostras = fs * duracao  
cutoffHigh = 60
cutoffLow = 30
opcao = '' # padrão


executando = False  
encerrar_programa = False

tempo = np.linspace(0, duracao, num_amostras, endpoint=False)

    # passa-baixa
def butter_lowpass(cutoff, fs, order):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    return b, a


def butter_lowpass_filter(sinalSomado, cutoff, fs, order):
    b, a = butter_lowpass(cutoff, fs, order)
    y = lfilter(b, a, sinalSomado)
    return y


    # passa-alta
def butter_highpass(cutoff, fs, order):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype="high", analog=False)
    return b, a


def butter_highpass_filter(data, cutoff, fs, order):
    b, a = butter_highpass(cutoff, fs, order)
    y = lfilter(b, a, data)
    return y


    # passa-faixa
def butter_bandpass(lowcut, highcut, fs, order):
    nyquist = 0.5 * fs  # Frequência de Nyquist
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band', analog=False)
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order):
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    y = lfilter(b, a, data)  # Aplica o filtro ao sinal
    return y


def calcularFFT(sinal, taxa_amostragem):
    N = len(sinal)
    fft_sinal = np.fft.fft(sinal)
    T = 1 / taxa_amostragem
    frequencias = np.fft.fftfreq(N, T)[: N // 2]
    amplitudes = np.abs(fft_sinal)[: N // 2] * (2 / N)
    indice_pico = np.argmax(amplitudes)
    frequencia_pico = frequencias[indice_pico]
    return frequencias, amplitudes, frequencia_pico


#controle do loop
def loop_principal():
    global executando, encerrar_programa

    while not encerrar_programa:
        if executando:
            print("Executando loop principal...")

           
            ser = serial.Serial(porta, baudrate)
            time.sleep(1)

            print("Iniciando captura de dados...")
            amostras = []
            while len(amostras) < num_amostras:
                if ser.in_waiting > 0:
                    linha = ser.readline().decode("utf-8", errors="ignore").strip()
                    if linha.isdigit():
                        valor = int(linha)
                        amostras.append(valor)
                    else:
                        print("Dado inválido:", linha)

            ser.close()
            print("Captura concluída. Conexão serial encerrada.")

            
            sinalCortado = butter_highpass_filter(amostras, 5, fs, order=6)
            SinalBaixo = butter_lowpass_filter(sinalCortado, cutoffLow, fs, order=6)
            sinalAlto = butter_highpass_filter(sinalCortado, cutoffHigh, fs, order=6)
            sinalFaixa = butter_bandpass_filter(sinalCortado, cutoffLow, cutoffHigh, fs, order=6)

            # Soma dos sinais
            
            
            
            somaBaixo = np.sum(np.abs(SinalBaixo))
            somaAlto = np.sum(np.abs(sinalAlto))
            somaCortado = np.sum(np.abs(sinalCortado))
            somaFaixa = np.sum(np.abs(sinalFaixa))

            print("soma do sinal: ", somaCortado)

            print("soma do sinal baixo: ", somaBaixo)

            print("Soma do sinal alto: ", somaAlto)

            

           
            frequencias_orig, amplitudes_orig, picoOriginal = calcularFFT(amostras, fs)
            frequencias_filt, amplitudes_filt, picoCortado = calcularFFT(sinalCortado, fs)
            freqBaixo, ampBaixo, picoBaixo = calcularFFT(SinalBaixo, fs)
            freqAlto, ampAlto, picoAlto = calcularFFT(sinalAlto, fs)
            freqFaixa, ampFaixa, picoFaixa = calcularFFT(sinalFaixa, fs)
            binValue = ""
            # Binário de possibilidades
            
            if somaBaixo > 60000 and somaAlto > 60000:
                print(f"Existem os sinais de 70hz (passa altas) e 15hz (passa baixas)")
                binValue = "11"
            elif somaBaixo < 60000 and somaAlto > 60000:
                print(f"Existe apenas o sinal de 70hz (passa altas)")
                binValue = "10"
            elif somaBaixo > 60000 and somaAlto < 60000:
                print(f"Existe apenas o sinal de 15hz (passa baixas)")
                binValue = "01"
            elif somaBaixo < 60000 and somaAlto < 60000:
                print("não existem sinais passando pelos filtros de passa baixa e passa alta")
                binValue = "00"   
            
            '''
            Formato de envio: X000
            A = 
            B =
            C = 
            D = 
            '''
            
           
            # opcao1 = opcao[0]
            # opcao2 = opcao[1]
            # binValue1 = binValue[0] 
            # binValue2 = binValue[1] 
           
            enviar = opcao + binValue + ";"
            print(opcao)
            print(binValue)
            # print('enviar para controlador: ', opcao1, opcao2, binValue1, binValue2)
            
            ser2 = serial.Serial("COM6", 9600)
            # opcao = 'D211'
            time.sleep(2)
            
            # ser2.write(opcao1.encode())
            # ser2.write(opcao2.encode())
            # ser2.write(binValue1.encode())
            # ser2.write(binValue2.encode())
            
            ser2.write(enviar.encode())
            
            print('ENVIADO')
            time.sleep(2)
            ser2.close()
            
            
            time.sleep(5)
            
            
           
            plt.figure(figsize=(12, 8)) 
            
            # sinal original
            
            plt.subplot(5, 2, 1)
            plt.plot(tempo, amostras, label="Sinal Recebido (Normalizado)")
            plt.title("Sinal Recebido")
            plt.xlabel("Tempo (s)")
            plt.ylabel("Amplitude")
            plt.grid()
            plt.legend()



            
            plt.subplot(5, 2, 2)
            plt.plot(frequencias_orig, amplitudes_orig, label="FFT Original")
            plt.title("FFT do sinal Original")
            plt.xlabel("Frequência (Hz)")
            plt.ylabel("Amplitude")
            plt.xlim(0, 100)
            plt.grid()
            plt.legend()

            # sinal cortado
                       
            plt.subplot(5, 2, 3)
            plt.plot(tempo, sinalCortado, label="Sinal Filtrado (Passa-Alta)", color="orange")
            plt.title("Sinal cortado")
            plt.xlabel("Tempo (s)")
            plt.ylabel("Amplitude")
            plt.grid()
            plt.legend()


            
            plt.subplot(5, 2, 4)
            plt.plot(frequencias_filt, amplitudes_filt, label="FFT Filtrado")
            plt.title("FFT do sinal Cortado")
            plt.xlabel("Frequência (Hz)")
            plt.ylabel("Amplitude")
            plt.xlim(0, 100)
            plt.grid()
            plt.legend()

            # sinal baixo

            plt.subplot(5, 2, 5)
            plt.plot(tempo, SinalBaixo, label="Sinal Filtrado (Passa-Alta)", color="orange")
            plt.title("Sinal Passa-Baixa")
            plt.xlabel("Tempo (s)")
            plt.ylabel("Amplitude")
            plt.grid()
            plt.legend()



            plt.subplot(5, 2, 6)
            plt.plot(freqBaixo, ampBaixo, label="FFT Original")
            plt.title("FFT do passa-baixa")
            plt.xlabel("Frequência (Hz)")
            plt.ylabel("Amplitude")
            plt.xlim(0, 100)
            plt.grid()
            plt.legend()

            # sinal alto
            
            plt.subplot(5, 2, 7)
            plt.plot(tempo, sinalAlto, label="Passa-Alta", color="orange")
            plt.title("Sinal Passa-Alta")
            plt.xlabel("Tempo (s)")
            plt.ylabel("Amplitude")
            plt.grid()
            plt.legend()

            plt.subplot(5, 2, 8)
            plt.plot(freqAlto, ampAlto, label="FFT Alta")
            plt.title("FFT do passa-alta")
            plt.xlabel("Frequência (Hz)")
            plt.ylabel("Amplitude")
            plt.xlim(0, 100)
            plt.grid()
            plt.legend()
            
            # sinal passa faixa
            
            plt.subplot(5, 2, 9)
            plt.plot(tempo, sinalFaixa, label="Passa-Faixa", color="orange")
            plt.title("Sinal Passa-Faixa")
            plt.xlabel("Tempo (s)")
            plt.ylabel("Amplitude")
            plt.grid()
            plt.legend()

            plt.subplot(5, 2, 10)
            plt.plot(freqFaixa, ampFaixa, label="FFT Faixa")
            plt.title("FFT do Passa-faixa")
            plt.xlabel("Frequência (Hz)")
            plt.ylabel("Amplitude")
            plt.xlim(0, 100)
            plt.grid()
            plt.legend()
            
            
            

            plt.tight_layout()
            plt.pause(10)
            plt.close('all')
            
        else:
            
            time.sleep(0.5)



def iniciar_tkinter():
    global executando, encerrar_programa
    def selecionar_opcao():
        global opcao
        opcao = selected_option.get()
        print(f"modo selecionada: {opcao}")
    

    
    def alternar_execucao():
        global executando
        executando = not executando
        if executando:
            botao_continuar_parar.config(text="Parar")
            print("Loop principal iniciado.")
        else:
            botao_continuar_parar.config(text="Continuar")
            print("Loop principal pausado.")

    
    def encerrar():
        global encerrar_programa
        encerrar_programa = True
        print("Encerrando programa...")
        root.destroy()

    
    root = tk.Tk()
    root.title("Controle do Loop")

    
    botao_continuar_parar = tk.Button(root, text="Continuar", command=alternar_execucao)
    botao_continuar_parar.pack(pady=10)

    
    botao_encerrar = tk.Button(root, text="Encerrar", command=encerrar)
    botao_encerrar.pack(pady=10)
    
    
    root.title("Escolha uma opção")


    selected_option = tk.StringVar()
    selected_option.set("A")  


    opcao1 = tk.Radiobutton(root, text="A - Economia de energia", variable=selected_option, value="A2")
    opcao1.pack(anchor=tk.W)

    opcao2 = tk.Radiobutton(root, text="B - Maior taxa de comunicação", variable=selected_option, value="C2")
    opcao2.pack(anchor=tk.W)

    opcao3 = tk.Radiobutton(root, text="C - Maior alcance", variable=selected_option, value="D2")
    opcao3.pack(anchor=tk.W)

    confirmar_botao = tk.Button(root, text="Confirmar", command=selecionar_opcao)
    confirmar_botao.pack()

        
    root.mainloop()



th.Thread(target=loop_principal, daemon=True).start()


iniciar_tkinter()
