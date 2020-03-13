#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import icc2
import os
icc=icc2.Icc()

nuevaCaja='GEMALTO-005'
nuevaAgencia='DXTRA'

while True:
   newiccid=input('Escribe ICCID: (X para terminar) ')
   if newiccid=='x':
      print('-----PROCESO FINALIZADO-----')
      exit()
   icc.id=newiccid
   if len(icc.id)==19 and icc.verificar():
      icc.encuentra()
      icc.agencia=nuevaAgencia
      icc.caja=nuevaCaja
      icc.estado='USADO'
      icc.guarda()
      os.system("play --no-show-progress --null -t alsa --channels 2 synth 0.15 sine 1800")
      if icc.cantidadEnCaja(icc.caja)>=100:
         icc.beepCajaLlena()
   else:
      os.system("play --no-show-progress --null -t alsa --channels 2 synth 0.1 sine 400")
      os.system("play --no-show-progress --null -t alsa --channels 2 synth 0.1 sine 400")
