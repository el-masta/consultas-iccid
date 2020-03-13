#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Clase y métodos para objeto ICC
#

from luhn import verify
from datetime import date
import os
import time
import sys
import re
from terminaltables import SingleTable
from colorclass import Color
import requests
from requests.auth import HTTPBasicAuth

dia = date.today()
hoy = dia.strftime("%Y-%m-%d")

#Trabaja con MongoDB
from pymongo import MongoClient
client = MongoClient('localhost',
                     username='*****',
                     password='*****',
                     authSource='Portas')
db = client.Portas.ICC

# Pegar texto de cookie
textcookie = 'Aqui se pega el texto de la cookie tal como aparece en el header despues de hacer login en el SMART'

#Establece variables para consulta
headers = {
    'user-agent':
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36"
}
# Arma array de cookies
arrCookies = textcookie.split(';')
objCookies = {}
for cookie in arrCookies:
    par = cookie.split('=')
    objCookies[par[0]] = par[1]


class Icc:
    '''Clase ICC'''
    id, agencia, creado, modificado, estado, caja, cantEnCaja, revisiones, portaciones ='','','','','','',0,[],[]

    #******** Metodos generales *********

    def limpia(self):
        '''Limpia los valores del ICC'''
        self.id = ''
        self.agencia = ''
        self.creado = ''
        self.modificado = ''
        self.estado = ''
        self.caja = ''
        self.cantEnCaja = ''
        self.revisiones = []
        self.portaciones = []

    def muestraDatos(self):
        '''Muestra datos completos de ICC'''
        #Aplica color al estado del ICCID
        estado = ''
        headertip = ''
        if self.estado == 'USADO' or self.estado == 'PORTADO' or self.estado == 'RESERVADO' or self.estado == 'REVISION':
            estado = Color('{hiyellow}' + self.estado + '{/yellow}')
            headertip = Color('{hibgyellow}  {/bgyellow}')
        elif self.estado == 'NUEVO' or self.estado == 'VALIDO':
            estado = Color('{higreen}' + self.estado + '{/green}')
            headertip = Color('{hibggreen}  {/bggreen}')
        else:
            estado = Color('{hired}' + self.estado + '{/red}')
            headertip = Color('{hibgred}  {/bgred}')
        #Imprime datos generales
        print(
            Color('{autobgblack}{hiwhite}' + self.id.center(78) +
                  '{/white}{/bgblack}') + headertip)
        print(Color('Agencia:\t{hicyan}' + self.agencia + '{/cyan}'))
        print('Creado:\t\t' + self.creado)
        print('Modificado:\t' + self.modificado)
        print('Estado:\t\t' + estado)
        print('Caja:\t\t' + self.caja + '  (' + str(self.cantEnCaja) + ')')
        #Imṕrime revisiones
        for revision in self.revisiones:
            print('\tRevisado:\t' + revision['fecha'] + '\tEstado:\t' +
                  revision['estado'])
        #Imṕrime portaciones
        for portacion in self.portaciones:
            print('\tPortado:\t' + portacion['fecha'] + '\tNumero:\t' +
                  portacion['numero'])
        print('\n')

    def encuentra(self):
        '''Encuentra un ICCID específico\n
      encuentra(iccid)\n
      Exito: True'''
        tempid = self.id
        self.limpia()
        self.id = tempid
        iccdb = db.find_one({'_id': self.id})
        if iccdb:
            self.agencia = iccdb['agencia']
            self.creado = iccdb['creado']
            self.modificado = iccdb['modificado']
            self.estado = iccdb['estado']
            self.caja = iccdb['caja']
            self.cantEnCaja = str(self.cantidadEnCaja(self.caja))
            if 'revisiones' in iccdb:
                self.revisiones = iccdb['revisiones']
            if 'portaciones' in iccdb:
                self.portaciones = iccdb['portaciones']
            if 'revision' in iccdb:
                print(
                    Color('{bgyellow}{hiblack}' + 'PARA REVISAR'.center(80) +
                          '{/black}{/bgyellow}'))
            self.muestraDatos()
            return True
        else:
            print(
                Color('{bgred}{hiwhite}' +
                      'NO SE ENCONTRO REGISTRO'.center(80) +
                      '{/white}{/bgred}'))
            print(
                Color('{bgred}{white}' + self.id.center(80) +
                      '{/white}{/bgred}'))
            print('')
            self.limpia()
            return False

    def cantidadEnCaja(self, findcaja):
        '''Obtiene la cantidad de chips en una caja'''
        return db.find({'caja': findcaja}).count()

    def guarda(self):
        '''Guarda Icc a base de datos, se requiere de Id, Agencia, Caja\n
      Si no existe, se crea nuevo registro\n
      Exito: True'''
        if self.agencia != '' or self.caja != '' or verify(self.id) == False:
            self.modificado = hoy
            existeRegistro = db.find_one({'_id': self.id})
            #Si existe registro
            if existeRegistro:
                #Revisa portacione y revisiones
                if 'revisiones' in existeRegistro:
                    self.revisiones = existeRegistro['revisiones']
                if 'portaciones' in existeRegistro:
                    self.portaciones = existeRegistro['portaciones']
                db.update_one({'_id': self.id}, {
                    '$set': {
                        'agencia': self.agencia,
                        'modificado': self.modificado,
                        'estado': self.estado,
                        'caja': self.caja,
                    }
                })
                print(
                    Color('{autobgblack}{hiyellow}' + 'GUARDADO'.center(80) +
                          '{/yellow}{/bgblack}'))
                self.cantEnCaja = str(self.cantidadEnCaja(self.caja))
                self.muestraDatos()
            else:
                #Si no existe registro, pone datos por default
                if self.estado == '':
                    self.estado = 'DESCONOCIDO'
                if self.creado == '':
                    self.creado = hoy
                db.insert_one({
                    "_id": self.id,
                    "agencia": self.agencia,
                    "creado": self.creado,
                    "modificado": self.modificado,
                    "estado": self.estado,
                    "caja": self.caja
                })
                print(
                    Color('{hibgyellow}{hiblack}' +
                          'REGISTRO CREADO'.center(80) +
                          '{/black}{/bgyellow}'))
                self.cantEnCaja = str(self.cantidadEnCaja(self.caja))
                self.muestraDatos()
            return True
        else:
            print(
                Color('{bgred}{hiwhite}' + 'NO SE PUDO GUARDAR'.center(50) +
                      '{/white}{/bgred}'))
            print(
                Color('{bgred}{hiwhite}' + 'DATOS INCOMPLETOS'.center(50) +
                      '{/white}{/bgred}'))
            return False

    def agregarRevision(self, estado):
        '''Agrega revisión a ICC, especificando estado'''
        self.revisiones.append({'fecha': hoy, 'estado': estado})
        self.estado = estado
        db.update_one({'_id': self.id}, {
            '$set': {
                'revisiones': self.revisiones
            },
            '$unset': {
                'revision': 1
            }
        })
        print('Revision agregada:\t' + estado)

    def marcaParaRevision(self):
        '''Marca el ICC para revisión'''
        db.update_one({'_id': self.id}, {'$set': {'revision': 'REVISAR'}})

    def agregarPortacion(self, fecha, numero):
        '''Agrega portación a ICC, especificando fecha y número'''
        self.portaciones.append({'fecha': fecha, 'numero': numero})
        db.update_one({'_id': self.id},
                      {'$set': {
                          'portaciones': self.portaciones
                      }})
        print('Portacion agregada:\t' + numero)

    #******** Metodos Específicos *********
    def encuentraParaRevision(self):
        '''Encuentra un ICCID para revisar\n
      encontrarParaRevision(caja)\n
      Exito: True'''
        self.limpia()
        iccdb = db.find_one({'revision': 'REVISAR'}, {'revision': 1})
        if iccdb:
            self.id = iccdb['_id']
            self.encuentra()
            return True
        else:
            print(
                Color('{bgred}{hiwhite}' +
                      'NO SE ENCONTRARON CHIPS PARA REVISAR'.center(80) +
                      '{/white}{/bgred}'))
            self.limpia()
            return False

    #Funciones varias
    def validosPorCaja(self):
        '''Muestra la cantidad de chips válidos en cajas'''
        pipeline = [{
            '$match': {
                'estado': 'VALIDO'
            }
        }, {
            '$group': {
                '_id': '$caja',
                'cantidad': {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                '_id': 1
            }
        }]
        cajas = list(db.aggregate(pipeline))
        #Crea tabla
        table_data = [[
            Color('{autocyan}Caja{/cyan}'),
            Color('{autocyan}Validos{/cyan}')
        ]]
        total = 0
        for caja in cajas:
            table_data.append([caja['_id'], caja['cantidad']])
            total += caja['cantidad']
        table_data.append([
            Color('{autocyan}Total:{/cyan}'),
            Color('{autocyan}' + str(total) + '{/cyan}')
        ])
        table = SingleTable(table_data)
        table.title = 'Validos por caja'
        table.justify_columns = {0: 'right'}
        print(table.table)

    def estadosEnCaja(self, nombrecaja):
        '''Muestra la cantidad de estados diferentes en una caja'''
        pipeline = [{
            '$match': {
                'caja': nombrecaja
            }
        }, {
            '$group': {
                '_id': '$estado',
                'cantidad': {
                    '$sum': 1
                }
            }
        }]
        estados = list(db.aggregate(pipeline))
        #Crea tabla
        table_data = [[
            Color('{autocyan}Estado{/cyan}'),
            Color('{autocyan}Cantidad{/cyan}')
        ]]
        total = 0
        for estado in estados:
            table_data.append([estado['_id'], estado['cantidad']])
            total += estado['cantidad']
        table_data.append([
            Color('{autocyan}Total:{/cyan}'),
            Color('{autocyan}' + str(total) + '{/cyan}')
        ])
        table = SingleTable(table_data)
        table.title = nombrecaja
        table.justify_columns = {0: 'right'}
        print(table.table)

    def revisionesPorCaja(self):
        '''Muestra la cantidad de chips por revisar en cajas'''
        pipeline = [{
            '$match': {
                'revision': 'REVISAR'
            }
        }, {
            '$group': {
                '_id': '$caja',
                'cantidad': {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                '_id': 1
            }
        }]
        cajas = list(db.aggregate(pipeline))
        #Crea tabla
        table_data = [[
            Color('{autocyan}Caja{/cyan}'),
            Color('{autocyan}Revisiones{/cyan}')
        ]]
        total = 0
        for caja in cajas:
            table_data.append([caja['_id'], caja['cantidad']])
            total += caja['cantidad']
        table_data.append([
            Color('{autocyan}Total:{/cyan}'),
            Color('{autocyan}' + str(total) + '{/cyan}')
        ])
        table = SingleTable(table_data)
        table.title = 'Revisiones por caja'
        table.justify_columns = {0: 'right'}
        print(table.table)

    def cajaParaRevisar(self):
        '''Identifica la caja siguente para revisar'''
        pipeline = [{
            '$match': {
                'caja': {
                    '$nin': ['VIRTUAL', 'ENTREGADO', 'PERDIDO']
                },
                'estado': {
                    '$in': ['USADO', 'RESERVADO', 'PORTADO']
                },
                'revision': {
                    '$nin': ['REVISAR']
                }
            }
        }, {
            '$sort': {
                'modificado': 1
            }
        }, {
            '$limit': 1
        }]
        cajas = list(db.aggregate(pipeline))
        for caja in cajas:
            print('Revisar la caja:\t' + caja['caja'])

    def marcarCajaRevision(self, nombrecaja):
        '''Marca una caja para revision'''
        db.update_many({'caja': {
            '$regex': '^' + nombrecaja
        }}, {'$set': {
            'revision': 'REVISAR'
        }})
        print('Cajas: ' + nombrecaja + ' marcadas para revision')

    def entrega(self, cantidad):
        '''Realiza entrega de una cantidad especifica de chips\n
      entrega(cantidad)'''
        for x in range(cantidad):
            iccdb = db.find_one({'agencia': 'Y-PARA-ENTREGA'})
            if iccdb:
                db.update_one({'_id': iccdb['_id']}, {
                    '$set': {
                        'agencia': 'Z-ENTREGADO',
                        'caja': 'ENTREGADO',
                        'estado': 'DEVUELTO'
                    }
                })
                print(str(x + 1) + '\t' + iccdb['_id'] + '\t Devuelto')

    def verificar(self):
        '''Verifica que el ID sea válido'''
        return verify(self.id)

    def consultaEstado(self, ):
        # Arma url de consulta y de cancelacion de reserva
        url = 'http://portabilidad.telcel.com/FormatoUnicoPrepagoWEB/app/ValidaImeiIccid.do?region=9&iccid=' + self.id 
        urlcancelacion = 'http://portabilidad.telcel.com/FormatoUnicoPrepagoWEB/app/CancelaReservaIccid.do?region=9&iccid=' + self.id
        #Realiza consulta
        respuesta = requests.get(url, headers=headers, cookies=objCookies).text

        if respuesta.find('3 - Reservado') > 0:
            #Cancelacion de reserva
            requests.get(urlcancelacion, headers=headers,
                         cookies=objCookies).text
            return 'RESERVADO', ''
        elif respuesta.find('1 - Usado') > 0:
            return 'USADO', ''
        elif respuesta.find('9 - Baja') > 0:
            return 'BAJA', ''
        elif respuesta.find('2 - Robo') > 0:
            return 'ROBO', ''
        elif respuesta.find('_codigoTelcel') > 0:
            requests.get(urlcancelacion, headers=headers,
                         cookies=objCookies).text
            return 'VALIDO', ''
        else:
            return 'DESCONOCIDO', respuesta

    def beepCajaLlena(self):
        os.system(
            "play --no-show-progress --null -t alsa --channels 2 synth 0.1 sine 800"
        )
        os.system(
            "play --no-show-progress --null -t alsa --channels 2 synth 0.1 sine 1000"
        )
        os.system(
            "play --no-show-progress --null -t alsa --channels 2 synth 0.1 sine 1200"
        )

    def beepSeparar(self):
        os.system(
            "play --no-show-progress --null -t alsa --channels 2 synth 0.25 sine 1800"
        )

    def beepMantener(self):
        os.system(
            "play --no-show-progress --null -t alsa --channels 2 synth 0.3 sine 800"
        )

    def beepRobo(self):
        os.system(
            "play --no-show-progress --null -t alsa --channels 2 synth 0.15 sine 1300"
        )
        os.system(
            "play --no-show-progress --null -t alsa --channels 2 synth 0.15 sine 1300"
        )
        os.system(
            "play --no-show-progress --null -t alsa --channels 2 synth 0.15 sine 1300"
        )

    def beepBaja(self):
        os.system(
            "play --no-show-progress --null -t alsa --channels 2 synth 0.15 sine 800"
        )
        os.system(
            "play --no-show-progress --null -t alsa --channels 2 synth 0.15 sine 800"
        )


icc = Icc()
#icc.marcarCajaRevision('WCM')
#icc.marcarCajaRevision('GEMALTO')
#icc.revisionesPorCaja()
#icc.cajaParaRevisar()
#icc.validosPorCaja()
#icc.entrega(179)
