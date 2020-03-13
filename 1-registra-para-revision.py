#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import icc
icc = icc.Icc()

agenciaSiEsNuevo = 'DESCONOCIDA'
cajaAsignada = 'GEMALTO-009'
cajaBaja = 'ORBERTHUR-027'
cajaRobo = 'VALID-024'

while True:
    icc.limpia()
    newiccid = input('Escribe ICCID: (X para terminar) ')
    if newiccid == 'x':
        print('-----PROCESO FINALIZADO-----')
        exit()
    icc.id = str(newiccid)
    if icc.verificar():
        #Si el chip NO está registrado
        if not icc.encuentra():
            # Registra y marca para revision
            icc.agencia = agenciaSiEsNuevo
            icc.caja = cajaAsignada
            icc.estado = 'DESCONOCIDO'
            icc.guarda()
            icc.marcaParaRevision()
            icc.beepSeparar()
            if icc.cantidadEnCaja(icc.caja) >= 100:
                icc.beepCajaLlena()
        else:

            # Cuando el chip está registrado como ROBO
            if icc.estado == 'ROBO':
                icc.beepRobo()
                icc.caja = cajaRobo
                icc.guarda()
                if icc.cantidadEnCaja(icc.caja) >= 100:
                    icc.beepCajaLlena()

            # Cuando el chip está registrado como BAJA
            elif icc.estado == 'BAJA':
                icc.beepBaja()
                icc.caja = cajaBaja
                icc.guarda()
                if icc.cantidadEnCaja(icc.caja) >= 100:
                    icc.beepCajaLlena()

            # Cuando el chip está registrado, lo marca para revision
            else:
                icc.marcaParaRevision()
                if icc.agencia == 'Z-ENTREGADO' or icc.agencia == 'Y-PARA-ENTREGA':
                    icc.agencia = agenciaSiEsNuevo
                icc.caja = cajaAsignada
                icc.estado = 'DESCONOCIDO'
                icc.guarda()
                icc.beepSeparar()
                if icc.cantidadEnCaja(icc.caja) >= 100:
                    icc.beepCajaLlena()
