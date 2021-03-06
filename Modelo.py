# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 12:56:57 2018

@author: SALASDRAI
"""
import numpy as np


class Biosenal(object):
    def __init__(self,data=None):
        if not data==None:
            self.asignarDatos(data)
        else:
            self.__data=np.asarray([])
            self.__canales=0
            self.__puntos=0
        self.__inicio = 0
        self.__final = 0
   
        
    def analizar_multitaper(self, senal1,fs,fpassi,fpassf,W,T,p):#analisis usando multitaper scipy 1.1.0
        
        from chronux.mtspectrumc import mtspectrumc        
        params = dict(fs = fs, fpass = [fpassi, fpassf], tapers = [W, T, p], trialave = 1)
        
        data = np.reshape(senal1,(fs*5,10),order='F')        
        #Calculate the spectral power of the data
        self.Pxx, self.f = mtspectrumc(data, params)        
        return(self.Pxx, self.f)
        
        
    def transf_wevelet(self,senal1,fs,fpassi,fpassf,nescalas):#analisis usando wavelet continuo
        import pywt #1.1.1
         
        N=senal1.shape[0];
        sampling_period =  1/fs
        Frequency_Band = [fpassi, fpassf] # Banda de frecuencia a analizar
        
        # Métodos de obtener las escalas para el Complex Morlet Wavelet  
        # Método 1:
        # Determinar las frecuencias respectivas para una escalas definidas
        scales = np.arange(1, nescalas)
        frequencies = pywt.scale2frequency('cmor', scales)/sampling_period
        # Extraer las escalas correspondientes a la banda de frecuencia a analizar
        scales = scales[(frequencies >= Frequency_Band[0]) & (frequencies <= Frequency_Band[1])] 

        # Obtener el tiempo correspondiente a una epoca de la señal (en segundos)
        time_epoch = sampling_period*N
        
        # Analizar una epoca de un montaje (con las escalas del método 1)
        # Obtener el vector de tiempo adecuado para una epoca de un montaje de la señal
        time = np.arange(0, time_epoch, sampling_period)
        # Para la primera epoca del segundo montaje calcular la transformada continua de Wavelet, usando Complex Morlet Wavelet
        
        [coef, freqs] = pywt.cwt(senal1, scales, 'cmor', sampling_period)
        # Calcular la potencia 
        power = (np.abs(coef)) ** 2
        return(time,freqs,power)
        
    

    

    
