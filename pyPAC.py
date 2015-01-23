#!/usr/bin/python
# -*- coding: utf-8 -*-
#~ '****************************************************************************
#~ '    CLASE PARA CONSUMIR LOS SERVICIOS DEL EXCELENTE PAC ECODEX
#~ '
#~ '    Copyright (C) 2012 Mauricio Baeza Servin
#~ '    Este programa es software libre. Puede redistribuirlo y/o modificarlo
#~ '    bajo los términos de la Licencia Pública General de GNU según es
#~ '    publicada por la Free Software Foundation, bien de la versión 3 de dicha
#~ '    Licencia o bien (según su elección) de cualquier versión posterior.
#~ '
#~ '    Este programa se distribuye con la esperanza de que sea útil, pero SIN
#~ '    NINGUNA GARANTÍA, incluso sin la garantía MERCANTIL implícita o sin
#~ '    garantizar la CONVENIENCIA PARA UN PROPÓSITO PARTICULAR.
#~ '    Véase la Licencia Pública General de GNU para más detalles.
#~ '
#~ '    Debería haber recibido una copia de la Licencia Pública General junto
#~ '    con este programa. Si no ha sido así, escriba a la Free Software
#~ '    Foundation, Inc., en 675 Mass Ave, Cambridge, MA 02139, EEUU.
#~ '
#~ '    Mauricio Baeza - correopublico ARROBA mauriciobaeza NET
#~ '
#~ '****************************************************************************

""" Class for webservices PAC ECODEX v3 for Python 3"""

import logging
import hashlib
import random
import base64
from pysimplesoap.client import SoapClient, SoapFault
from settings import DEBUG, LOG, PAC, WS


log = logging.getLogger(LOG['NAME'])


class ECODEX(object):
    _rfc_integrador = 'TU_RFC'
    _id_integrador = PAC['id_com']
    _id_alta_emisor = ''
    _url = 'https://serviciosnominas.ecodex.com.mx:4043/Servicio{}.svc?wsdl'
    _url_up = 'https://integradexnominas.ecodex.com.mx/Certificados/' \
        'Upload?UUID={{}}'
    if DEBUG:
        _rfc_integrador = 'BBB010101001'
        _id_integrador = PAC['id_test']
        _id_alta_emisor = ''
        _url = 'https://pruebas.ecodex.com.mx:2045/Servicio{}.svc?wsdl'
    _service_seguridad = ''
    _service_comprobantes = ''
    _service_timbrado = ''
    _service_repositorio = ''
    _service_clientes = ''
    _service_cancelacion = ''

    def __init__(self, rfc):
        self.rfc = rfc
        self.error = ''
        self.xml_send = ''
        self.xml = ''
        self.qr = None
        self._config_urls()

    def _config_urls(self):
        services = (
            'Seguridad',
            'Comprobantes',
            'Timbrado',
            'Repositorio',
            'Clientes',
            'Cancelacion'
        )
        for s in services:
            setattr(self,
                '_service_{}'.format(s.lower()), self._url.format(s))
        return

    def _get_token(self, id_transaccion=0, new_emisor=False):
        try:
            client = SoapClient(
                wsdl=self._service_seguridad,
                ns=WS['PREFIX_NS'],
                soap_ns=WS['PREFIX_SOAP'],
                timeout=WS['TIMEOUT'],
                trace=WS['TRACE'],
                cache=WS['CACHE'],
            )
            if new_emisor:
                rfc = self._rfc_integrador
            else:
                rfc = self.rfc
            retval = client.ObtenerToken(TransaccionID=id_transaccion, RFC=rfc)
            if new_emisor:
                s = '{}|{}|{}'.format(
                    self._id_integrador,
                    self._id_alta_emisor,
                    retval['Token']
                )
            else:
                s = '{}|{}'.format(self._id_integrador, retval['Token'])
            token_usuario = hashlib.sha1(s.encode()).hexdigest()
            return token_usuario
        except SoapFault as sf:
            self.error = sf.faultstring
            log.debug(self.error)
            return False
        except Exception as e:
            self.error = 'Se agoto el tiempo de espera'
            log.error('Token: ', exc_info=True)
            return False

    def timbrar(self, id_cfdi=0):
        """
        Siempre establece un id_transaccion que puedas recuperar en tu base de
        datos, si algo falla, se usa para consultar el estatus del documento.
        """
        id_transaccion = random.randint(1, 1000000000)
        if id_cfdi:
            id_transaccion = id_cfdi
        token = self._get_token(id_transaccion)
        if not token:
            return False
        try:
            log.info('Transaccion ID: {}'.format(id_transaccion))
            metodo = 'TimbraXML'
            xml = self.xml_send.encode("ascii", "xmlcharrefreplace")
            xml = xml.decode('utf-8')
            client = SoapClient(
                wsdl=self._service_timbrado,
                ns=WS['PREFIX_NS'],
                soap_ns=WS['PREFIX_SOAP'],
                timeout=WS['TIMEOUT'],
                trace=WS['TRACE'],
                cache=WS['CACHE'],
            )
            retval = getattr(client, metodo)(
                ComprobanteXML={'DatosXML': xml},
                RFC=self.rfc,
                Token=token,
                TransaccionID=id_transaccion
            )
            self.xml = retval['ComprobanteXML']['DatosXML']
            return True
        except SoapFault as sf:
            self.error = sf.faultstring
            log.debug(self.error)
            return False
        except Exception as e:
            self.error = 'Se agoto el tiempo de espera'
            log.error('Timbrado: ', exc_info=True)
            return False
