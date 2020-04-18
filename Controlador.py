#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 10:37:41 2018

@author: alexander
"""
from Modelo import Biosenal
from interfaz import InterfazGrafico
#para la ejecucion del programa
import sys
#QApplication controla la ejecución de los programas basados en interfaz
from PyQt5.QtWidgets import QApplication
class Principal(object):
    def __init__(self):        
        self.__app=QApplication(sys.argv)
        self.__mi_vista=InterfazGrafico()
        self.__mi_biosenal=Biosenal()
        self.__mi_controlador=Coordinador(self.__mi_vista,self.__mi_biosenal)
        self.__mi_vista.asignar_Controlador(self.__mi_controlador)
    def main(self):
        self.__mi_vista.show()
        sys.exit(self.__app.exec_())

    
class Coordinador(object):
    #como el coordindor enlaza el modelo con la vista debe
    #tener acceso a objetos de ambas clases
    def __init__(self,vista,biosenal):
        self.__mi_vista=vista
        self.__mi_biosenal=biosenal
 
    def analizar_multitaper(self, senal,fs,fpassi,fpassf,W,T,p):
        Pxx,f=self.__mi_biosenal.analizar_multitaper(senal,fs,fpassi,fpassf,W,T,p)
        return(Pxx,f)
    def transf_wevelet(self,senal1,fs,fpassi,fpassf,nescalas):
        time,freqs,power=self.__mi_biosenal.transf_wevelet(senal1,fs,fpassi,fpassf,nescalas)
        return(time,freqs,power)
    

        
p=Principal()
p.main()