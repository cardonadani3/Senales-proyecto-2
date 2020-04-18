# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 13:08:08 2020

@author: LENOVO
"""

#PRIMERA PARTE CARGA Y MANIPULACION BASICA

#library to load mat files
import scipy.io as sio;
import matplotlib.pyplot as plt;
import numpy as np;

from IPython import get_ipython

get_ipython().run_line_magic('matplotlib', 'qt')

#loading data
mat_contents = sio.loadmat('dataset_senales.mat')
#the data is loaded as a Python dictionary
print("the loaded keys are: " + str(mat_contents.keys()));
#in the current case the signal is stored in the data field
ojos_cerrados = np.squeeze(mat_contents['ojos_cerrados']); #to explain
ojos_abiertos = np.squeeze(mat_contents['ojos_abiertos']);
anestesia = np.squeeze(mat_contents['anestesia']);

plt.plot(ojos_cerrados)
plt.show()

#%%Transformada de Fourier
from scipy.fftpack import fft;

fs = 250
N = ojos_cerrados.shape[0];
#FREQUENCY RESOLUTION AND SAMPLING EFFECT OVER THE SPECTRA(to explain)
fs_res = fs/N

#frequency resolution fs/N
X = fft(ojos_cerrados);
freqs = np.arange(0.0, fs, fs_res);

get_ipython().run_line_magic('matplotlib', 'qt')

plt.plot(freqs, np.abs(X));
plt.show();

#FREQUENCY RESOLUTION AND SAMPLING EFFECT OVER THE SPECTRA(to explain)
#DC LEVELS
#%%se elimina el efecto del la baja frecuencia
ojos_cerrados = ojos_cerrados - np.mean(ojos_cerrados)
ojos_abiertos = ojos_abiertos - np.mean(ojos_abiertos)

#frequency resolution fs/N
X = fft(ojos_cerrados);
freqs = np.arange(0.0, fs, fs_res);

get_ipython().run_line_magic('matplotlib', 'qt')
plt.plot(freqs, np.abs(X));
plt.show();

#DC LEVELS

#%%analisis usando welch
import scipy.signal as signal;
#signal.welch(x, fs=1.0, window='hann', nperseg=None, noverlap=None, nfft=None, 
#detrend='constant', return_onesided=True, scaling='density', axis=-1)
f, Pxx = signal.welch(ojos_cerrados,fs,'hamming', fs*5, fs*2.5, scaling='density');
print(f.shape)
plt.plot(f[(f >= 4) & (f <= 40)],Pxx[(f >= 4) & (f <= 40)])
plt.show()




