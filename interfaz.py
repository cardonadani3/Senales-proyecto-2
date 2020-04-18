#%%ñibrerias
import sys
#Qfiledialog es una ventana para abrir yu gfuardar archivos
#Qvbox es un organizador de widget en la ventana, este en particular los apila en vertcal
from PyQt5.QtWidgets import  QMessageBox, QApplication, QMainWindow, QVBoxLayout, QFileDialog, QSpinBox, QPlainTextEdit,QMessageBox, QListWidget,QListWidgetItem
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIntValidator
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os 

from PyQt5.uic import loadUi

from numpy import arange, sin, pi
#contenido para graficos de matplotlib
from matplotlib.backends. backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import scipy.io as sio
import numpy as np
from Modelo import Biosenal
from csv import reader as reader_csv;
import scipy.signal as signal;  

# clase con el lienzo (canvas=lienzo) para mostrar en la interfaz los graficos matplotlib, el canvas mete la grafica dentro de la interfaz
class MyGraphCanvas(FigureCanvas):
    #constructor
    def __init__(self, parent= None,width=2, height=1, dpi=20):
        
        #se crea un objeto figura
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #el axes en donde va a estar mi grafico debe estar en mi figura
        self.axes = self.fig.add_subplot(111)
        
        #llamo al metodo para crear el primer grafico
        self.compute_initial_figure()
        
        #se inicializa la clase FigureCanvas con el objeto fig
        FigureCanvas.__init__(self,self.fig)

                  
    #este metodo me grafica al senal senoidal que yo veo al principio, mas no senales
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t,s,'m')
        self.axes.set_xlabel("muestras")
        self.axes.set_ylabel("voltaje (uV)")
    #hay que crear un metodo para graficar lo que quiera
    
        
    #Este metodo se encargara de todas las graficas de las senales, recibe los datos
    #a graficar
    def graficar_gatos(self,x,datos,labelx,labely):
        #primero se necesita limpiar la grafica anterior
        self.axes.clear()
        #ingresamos los datos a graficar
        #Se pone esta condicion para cuando haya que graficar un solo canal
        if datos.ndim ==1:
            self.axes.plot(x,datos)
        #Y tambien se puede usar cuando tenga que graficar muchos canales 
        else:
            DC = 10
            for c in range(datos.shape[0]):
                self.axes.plot(x,datos[c,:] + DC*c)
        self.axes.set_xlabel(labelx)
        self.axes.set_ylabel(labely)
        self.axes.figure.canvas.draw()
        #self.axes.set_title('Se�al')
    def graficar_scalogram(self,time,freqs,power,desde,hasta):
        # Graficar el escalograma obtenido del an�lisis tiempo frecuencia
        self.axes.clear()        
        scalogram = self.axes.contourf(time,
                         freqs[(freqs >= desde) & (freqs <= hasta)],
                         power[(freqs >= desde) & (freqs <= hasta),:],
                         100, # Especificar 20 divisiones en las escalas de color 
                         extend='both')
        self.axes.set_ylabel('Frecuencia [Hz]')
        self.axes.set_xlabel('Tiempo [s]')
        

        self.fig.colorbar(scalogram)
        self.axes.figure.canvas.draw()

        
#%%
        #es una clase que yop defino para crear los intefaces graficos
class InterfazGrafico(QMainWindow):
    #condtructor
    def __init__(self):
        #siempre va el constructor
        super(InterfazGrafico,self).__init__()
        #se carga el diseno creado en qt
        loadUi ('anadir_grafico - copia.ui',self)
        #loadUi ('anadir_graf.ui',self)
        
        #se llama la rutina donde configuramos la interfaz
        self.setup()
        #se muestra la interfaz
        self.show()
    def setup(self):
        #los layout permiten organizar widgets en un contenedor
        #esta clase permite añadir widget uno encima del otro (vertical)
        layout = QVBoxLayout()

        #se añaden los dos  organizadores de grafico, uno sera para la senal origianal
        #y otro para la senal filtrada
        self.campo_grafico_2.setLayout(layout)
        self.campo_grafico.setLayout(layout)
        #se crea un objeto para manejo de graficos de las dos senales (original y 
        #filtrada)
        self.__sc = MyGraphCanvas(self.campo_grafico_2, width=10, height=8, dpi=100)
        self.__mc = MyGraphCanvas(self.campo_grafico, width=10, height=8, dpi=100)
        #se añade el campo de graficos para ambas senales
        layout.addWidget(self.__sc)
        layout.addWidget(self.__mc)
        #Se valida que los valores de tiempo puedan ser solo numeros y se da un 
        #rango que funcione para las se;ales cargadas
        self.boton_tiempo_inicial.setValidator(QIntValidator(1,99999))
        self.boton_tiempo_final.setValidator(QIntValidator(1,99999))

    
        #se organizan los botones que van conectados a los diferentes funciones
        self.boton_cargar.clicked.connect(self.cargar_senal)
        self.boton_analizar.clicked.connect(self.analizar)
        self.boton_welch.clicked.connect(self.analisis_welch)      
        self.boton_multitaper.clicked.connect(self.analisis_multitaper) 
        self.boton_wavelet.clicked.connect(self.analisis_wavelet)         
 
        #hay botones que no deberian estar habilitados si no he cargado la senal
       
        self.boton_tiempo_inicial.setEnabled(False)        
        self.boton_tiempo_final.setEnabled(False) 
        self.boton_fs.setEnabled(False)    
        self.boton_fpassi.setEnabled(False)          
        self.boton_fpassf.setEnabled(False) 
        self.boton_nperseg.setEnabled(False)         
        self.boton_w.setEnabled(False) 
        self.boton_p.setEnabled(False)
        self.boton_noverlap.setEnabled(False)        
        self.boton_ventana.setEnabled(False)
        self.boton_nescalas.setEnabled(False)
        self.boton_welch.setEnabled(False)
        self.boton_multitaper.setEnabled(False) 
        self.boton_wavelet.setEnabled(False)  
        
                     
        
        #cuando cargue la senal debo volver a habilitarlos
        
        #asigno el coordinador de todo el programa, une el modelo y la interfaz
    def asignar_Controlador(self,controlador):
        self.__coordinador=controlador
        
    def cargar_senal(self):
        #se abre el cuadro de dialogo para cargar
        #* son archivos .mat
        archivo_cargado, _ = QFileDialog.getOpenFileName(self, "Abrir señal","","Todos los archivos (*);;Archivos mat (*.mat)*;;Text files (.txt)*")
        if archivo_cargado != "":
            print(archivo_cargado)
            mate =(str(archivo_cargado)).find(".mat")
            openbci =(str(archivo_cargado)).find(".txt")
            #Se utiliza este condicional para garantizar que se carguen dos tipos 
            #senales, tanto en openbci como en .mat
            if mate == -1 and openbci == -1:
                print('cargue un archivo compatible')
            elif mate != -1:
                data = sio.loadmat(archivo_cargado)
                self.data = np.squeeze(data["data"])
                x=np.arange(len(self.data+1))
                self.__sc.graficar_gatos(x,self.data,'Muestras','Voltaje')
                
        self.boton_welch.setEnabled(True)
        self.boton_multitaper.setEnabled(True) 
        self.boton_wavelet.setEnabled(True)                                         

        
    def analisis_welch(self):#Inhabilita los botones que no son necesarios para el analisis de welch
        self.boton_tiempo_inicial.setEnabled(True)        
        self.boton_tiempo_final.setEnabled(True) 
        self.boton_fs.setEnabled(True)    
        self.boton_fpassi.setEnabled(False)          
        self.boton_fpassf.setEnabled(False) 
        self.boton_nperseg.setEnabled(True)         
        self.boton_w.setEnabled(False) 
        self.boton_p.setEnabled(False)
        self.boton_noverlap.setEnabled(True)                  
        self.boton_ventana.setEnabled(True)
        self.boton_nescalas.setEnabled(False)
        self.analisis=1
      

    def analisis_multitaper(self):#Inhabilita los botones que no son necesarios para el analisis multitaper        
        self.boton_tiempo_inicial.setEnabled(True)        
        self.boton_tiempo_final.setEnabled(True) 
        self.boton_fs.setEnabled(True)    
        self.boton_fpassi.setEnabled(True)          
        self.boton_fpassf.setEnabled(True) 
        self.boton_nperseg.setEnabled(True)         
        self.boton_w.setEnabled(True) 
        self.boton_p.setEnabled(True)
        self.boton_noverlap.setEnabled(False)             
        self.boton_ventana.setEnabled(False) 
        self.boton_nescalas.setEnabled(False)
        self.analisis=2 

        
    def analisis_wavelet(self):#Inhabilita los botones que no son necesarios para el analisis de wavelt
        self.boton_tiempo_inicial.setEnabled(True)        
        self.boton_tiempo_final.setEnabled(True) 
        self.boton_fs.setEnabled(True)    
        self.boton_fpassi.setEnabled(True)          
        self.boton_fpassf.setEnabled(True) 
        self.boton_nperseg.setEnabled(False)         
        self.boton_w.setEnabled(False) 
        self.boton_p.setEnabled(False)
        self.boton_noverlap.setEnabled(False)             
        self.boton_ventana.setEnabled(False) 
        self.boton_nescalas.setEnabled(True)
        self.analisis=3           
            
    def analizar(self):        

        try:            
            self.fs= int(self.boton_fs.text())          
            self.desde=int(self.boton_tiempo_inicial.text())
            self.hasta=int(self.boton_tiempo_final.text())

            
            
            if self.analisis == 1:#llama la funcion que hace el analisis de welch
                import scipy.signal as signal1;                
                f, Pxx = signal1.welch(self.data,self.fs,self.boton_ventana.currentText(),int(self.boton_nperseg.text()), (int(self.boton_noverlap.text())/100)*int(self.boton_nperseg.text()), scaling='density');
                self.__mc.graficar_gatos(f[(f >= self.desde) & (f <= self.hasta)],Pxx[(f >= self.desde) & (f <= self.hasta)],'Frecuencia','Potencia')
                
        
            elif self.analisis==2: #llama la funcion que hace el analisis multitaper
                Pxx,f=self.__coordinador.analizar_multitaper(self.data,self.fs,float(self.boton_fpassi.text()),float(self.boton_fpassf.text()),float(self.boton_w.text()),int(self.boton_nperseg.text()),float(self.boton_p.text()));
                self.__mc.graficar_gatos(f[(f >= self.desde) & (f <= self.hasta)],Pxx[(f >= self.desde) & (f <= self.hasta)],'Frecuencia','Potencia')
                
            elif self.analisis==3:#llama la funcion que hace el analisis de wavelet continua
                time,freqs,power=self.__coordinador.transf_wevelet(self.data,self.fs,float(self.boton_fpassi.text()),float(self.boton_fpassf.text()),int(self.boton_nescalas.text()))
                self.__mc.graficar_scalogram(time,freqs,power,self.desde,self.hasta)
               
       
        except ValueError:      
            advertencia=QMessageBox()
            advertencia.setWindowTitle('Error')
            advertencia.setText('Recuerde llenar todos los espacios.\n SOLAMENTE valores numericos')
            advertencia.exec_()
  
                

            
                


    
                
    