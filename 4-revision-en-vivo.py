#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Revision de iccid
#  Leyendo de la pistola y
#  haciendo request sobre la API de Telcel

import icc
icc = icc.Icc()

while True:
    icc.limpia()
    newiccid = input('Escribe ICCID: (X para terminar) ')
    if newiccid == 'x':
        print('-----PROCESO FINALIZADO-----')
        exit()

    icc.id = newiccid

    if icc.verificar():
        icc.encuentra()
        icc.id = newiccid
        icc.caja = 'ENTREGADO'
        icc.agencia = 'DESCONOCIDA'

        estado, respuesta = icc.consultaEstado()

        if estado == 'DESCONOCIDO':
            print('*****ESTADO DESCONOCIDO*****')
            print(respuesta)
            icc.beepCajaLlena()
        elif estado == 'RESERVADO':
            print('*****Reservado, intentando liberar*****')
            icc.beepCajaLlena()
        elif estado == 'VALIDO':
            icc.beepSeparar()
            icc.agregarRevision(estado)
            icc.estado = 'DESCONOCIDO'
            icc.guarda()
        elif estado == 'ROBO':
            icc.beepRobo()
            icc.agregarRevision(estado)
            icc.estado = 'DESCONOCIDO'
            icc.guarda()
        elif estado == 'BAJA':
            icc.beepBaja()
            icc.agregarRevision(estado)
            icc.estado = 'DESCONOCIDO'
            icc.guarda()
        else:
            icc.beepMantener()
            icc.agregarRevision(estado)
            icc.estado = 'DESCONOCIDO'
            icc.guarda()
