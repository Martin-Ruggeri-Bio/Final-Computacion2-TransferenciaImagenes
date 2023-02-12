import random
import math

class Neurona():
    def __init__(self, cant_entradas):
        self.cant_entradas = cant_entradas + 1
        self.entradas = []
        self.pesos = [random.uniform(-1, 1) for i in range(self.cant_entradas)]
        self.salida_esperada = 0
        self.salida_real = 1
        self.delta = 0
        self.raning_rate = 0.5
        self.error = 0

    def asignar_entrada(self, entradas):
        self.entradas = entradas
        self.entradas.append(1)

    def entrenamiento(self, delta=0):
        if delta:
            delta_oculto = self.salida_real*(1-self.salida_real)*delta
            for i in range(self.cant_entradas):
                self.pesos[i] = self.pesos[i] + (self.raning_rate * self.entradas[i] * delta_oculto)
        x = 0
        for i in range(self.cant_entradas):
            x += self.entradas[i] * self.pesos[i]
        return 1/(1+math.exp(-x))
    
    def entrenamiento_back_final(self):
        self.salida_real = self.entrenamiento()
        self.error = self.salida_esperada - self.salida_real
        self.delta = self.salida_real*(1-self.salida_real)*self.error
        for i in range(self.cant_entradas):
            self.pesos[i] = self.pesos[i] + (self.raning_rate * self.entradas[i] * self.delta)

    def __str__(self):
        return (f"""
            entradas: {self.entradas}
            pesos: {self.pesos}
            salida_esperada: {self.salida_esperada}
            delta: {self.delta}
            salida_real: {self.salida_real}
        """)
