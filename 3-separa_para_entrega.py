#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import icc
icc = icc.Icc()

agenciaOk = 'Y-PARA-ENTREGA'
cajaBaja = 'VALID-008'
cajaRobo = 'VALID-005'
cajaUsado = 'WCM-033'
cajaLectura = ''

archivo = '/home/mario/Escritorio/Scripts Portas/validos_en_pila.dat'
f = open(archivo, 'r')
validos = int(f.read())
print('*************************Validos en pila: ' + str(validos))
f.close()


def resetPila():
    global validos
    validos = 0
    f = open(archivo, 'w')
    f.write('0')
    f.close()


def cambioDeCaja(caja):
    global cajaUsado
    cajaUsado = caja
    print('Se cambio la caja para usados a:' + caja)


while True:
    icc.limpia()
    newiccid = input('Escribe ICCID: (X para terminar) ')
    if newiccid == 'x':
        print('-----PROCESO FINALIZADO-----')
        f = open(archivo, 'w')
        f.write(str(validos))
        f.close()
        print('*************************Validos en pila: ' + str(validos))
        exit()
    # para mostrar datos varios
    if newiccid == 'v':
        icc.validosPorCaja()
        newiccid = '555'
    if newiccid == 'm':
        icc.estadosEnCaja(cajaLectura)
        newiccid = '555'
    if newiccid == 'r':
        resetPila()
        newiccid = '555'
    if newiccid == 'c':
        cambioDeCaja(cajaLectura)
        newiccid = '555'

    icc.id = newiccid
    if icc.verificar():
        icc.encuentra()
        cajaLectura = icc.caja

        # Cuando el chip no está registrado
        if icc.agencia == '':
            icc.beepCajaLlena()

        # Cuando el chip es válido
        if icc.estado == 'VALIDO' or icc.agencia == agenciaOk:
            print("\n********** Apartar chip **********")
            icc.beepSeparar()
            icc.agencia = agenciaOk
            icc.estado = 'DEVUELTO'
            icc.caja = 'ENTREGADO'
            icc.guarda()
            validos += 1
            print('*******************************CHIPS VALIDOS EN PILA: ' +
                  str(validos))
            if validos >= 50:
                icc.beepCajaLlena()
                icc.beepSeparar()
                icc.beepSeparar()
                validos = 0

        # Cuando el chip está marcado como ROBO
        elif icc.estado == 'ROBO':
            icc.beepRobo()
            icc.caja = cajaRobo
            icc.guarda()
            if icc.cantidadEnCaja(icc.caja) >= 100:
                icc.beepCajaLlena()

        # Cuando el chip está marcado como BAJA
        elif icc.estado == 'BAJA':
            icc.beepBaja()
            icc.caja = cajaBaja
            icc.guarda()
            if icc.cantidadEnCaja(icc.caja) >= 100:
                icc.beepCajaLlena()

        # Cuando el chip esta marcado como USADO, RESERVADO o era VIRTUAL
        elif icc.estado == 'USADO' or icc.estado == 'RESERVADO' or icc.caja == 'VIRTUAL' or icc.estado == 'PORTADO':
            print("\n\tMantener chip")
            icc.beepMantener()
            icc.caja = cajaUsado
            icc.guarda()
            if icc.cantidadEnCaja(icc.caja) >= 100:
                icc.beepCajaLlena()

        # Cuando el chip es de reingreso
        elif icc.estado == 'DEVUELTO' and icc.agencia != agenciaOk:
            print("\n\tMantener chip")
            icc.agencia = 'DESCONOCIDA'
            icc.marcaParaRevision()
            icc.beepMantener()
            icc.caja = cajaUsado
            icc.estado = 'DESCONOCIDO'
            icc.guarda()
            if icc.cantidadEnCaja(icc.caja) >= 100:
                icc.beepCajaLlena()

        # Cuando el chip está registrado pero no se ha procesado
        elif icc.estado == 'NUEVO':
            print("\n\tMantener chip")
            icc.beepMantener()
            icc.caja = cajaUsado
            icc.guarda()
            if icc.cantidadEnCaja(icc.caja) >= 100:
                icc.beepCajaLlena()
        else:
            pass
