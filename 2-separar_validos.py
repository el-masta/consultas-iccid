#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Revision de iccid
#  Leyendo de la base de datos y
#  haciendo request sobre la API de Telcel
import icc
icc = icc.Icc()

nuevoicc = True
bucle = True

while bucle == True:
    if nuevoicc == True:
        icc.encuentraParaRevision()
    if icc.id == '':
        bucle = False
        exit()
    estado, respuesta = icc.consultaEstado()
    if estado == 'DESCONOCIDO':
        print('*****ESTADO DESCONOCIDO*****')
        print(respuesta)
        bucle = False
    elif estado == 'RESERVADO':
        print('*****Reservado, intentando liberar*****')
        nuevoicc = False
    else:
        icc.estado = estado
        icc.agregarRevision(estado)
        icc.guarda()
        nuevoicc = True
