# -*- coding: utf-8 -*-

DEBUG = True
PAC = {
    'id_test': '2b3a8764-d586-4543-9b7e-82834443f219',
    'id_com': '',
}
LOG = {
    'NAME': 'CFDI',
    'FORMAT': '%(asctime)s-%(name)s-%(levelname)s - %(message)s',
    'DATE': '%d/%m/%Y %H:%M:%S',
    'FILE': 'debug.log',
}
WS = {
    'PREFIX_NS': 'cfdi',
    'PREFIX_SOAP': 'soapenv',
    'CACHE': False,
    'TIMEOUT': 25,
    'TRACE': False,
}
VERSION = '3.2'
TIPO_COMPROBANTE = ('ingreso', 'egreso', 'traslado')
SCHEMA = 'http://www.sat.gob.mx/cfd/3 ' \
    'http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd'
PREFIX = {
    '3.2': '{http://www.sat.gob.mx/cfd/3}',
    'TIMBRE': '{http://www.sat.gob.mx/TimbreFiscalDigital}',
}



