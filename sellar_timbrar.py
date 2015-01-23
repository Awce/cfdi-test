import logging
import os
from xml.etree import ElementTree as ET
import datetime
import time
import subprocess
from pyPAC import ECODEX as PAC
from settings import DEBUG, LOG, VERSION, TIPO_COMPROBANTE, SCHEMA, PREFIX


formatter = logging.Formatter(LOG['FORMAT'], datefmt=LOG['DATE'])
logging.basicConfig(
    level=logging.DEBUG, format=LOG['FORMAT'], datefmt=LOG['DATE'])
log = logging.getLogger(LOG['NAME'])
handler = logging.FileHandler(LOG['FILE'])
handler.setFormatter(formatter)
if DEBUG:
    handler.setLevel(logging.DEBUG)
else:
    handler.setLevel(logging.INFO)
log.addHandler(handler)


def call(args):
    return subprocess.check_output(args, shell=True).decode()

def get_cer():
    path = os.path.join(os.getcwd(), 'util/ecodex.cer')
    args = 'openssl enc -base64 -in {}'.format(path)
    return call(args).replace('\n','')

def get_serie():
    path = os.path.join(os.getcwd(), 'util/ecodex.cer')
    args = 'openssl x509 -inform DER -in {} -noout -serial'.format(path)
    return call(args).split('=')[1][1::2]

def get_sello(path_fac):
    path_cadena = os.path.join(os.getcwd(), 'util/cadena3.2.xslt')
    path_pem = os.path.join(os.getcwd(), 'util/ecodex.key.pem')
    args = 'xsltproc {0} {1} | openssl dgst -sha1 -sign {2} | ' \
        'openssl enc -base64 -A'.format(path_cadena, path_fac, path_pem)
    return call(args)

def get_epoch(date):
    e = int(time.mktime(date.timetuple()))
    return e


if __name__ == '__main__':
    if not os.path.exists('timbradas'):
        os.mkdir('timbradas')
    #~ Atributos mínimos para un CFDI valido "técnicamente"
    now = datetime.datetime.now()
    id_cfdi = get_epoch(now)
    atributos = {
        'cfdi': {
            'xmlns:cfdi': 'http://www.sat.gob.mx/cfd/3',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': SCHEMA,
            'version': VERSION,
            'fecha': now.isoformat()[:19],
            'tipoDeComprobante': TIPO_COMPROBANTE[0],
            'certificado': get_cer(),
            'noCertificado': get_serie(),
            'LugarExpedicion': 'Benito Juarez, México, D.F.',
            'formaDePago': 'Pago en una sola exhibición',
            'metodoDePago': 'Trueque',
            'subTotal': '1000.00',
            'total': '1000.00',
        },
        'emisor': {
            'rfc': 'AAA010101AAA',
        },
        'regimen': {
            'Regimen': 'Regimen de los esclavos del SAT',
        },
        'receptor': {
            'rfc': 'GGC890216AA6',
        },
        'conceptos': (
            {'cantidad': '1.0',
            'descripcion': 'Asesoría en desarrollo',
            'importe': '1000.00',
            'unidad': 'Servicio',
            'valorUnitario': '1000.00'},
        )
    }
    #~ Creamos el XML
    cfdi = ET.Element('cfdi:Comprobante', atributos['cfdi'])
    emisor = ET.SubElement(cfdi, 'cfdi:Emisor', atributos['emisor'])
    ET.SubElement(emisor, 'cfdi:RegimenFiscal', atributos['regimen'])
    receptor = ET.SubElement(cfdi, 'cfdi:Receptor', atributos['receptor'])
    conceptos = ET.SubElement(cfdi, 'cfdi:Conceptos')
    for c in atributos['conceptos']:
        ET.SubElement(conceptos, 'cfdi:Concepto', c)
    ET.SubElement(cfdi, 'cfdi:Impuestos')
    xml = ET.tostring(cfdi, encoding="unicode")
    with open('fac_temp.xml', 'w') as f:
        f.write(xml)
    cfdi.attrib['sello'] = get_sello('fac_temp.xml')
    xml = ET.tostring(cfdi, encoding="unicode")
    with open('fac_temp.xml', 'w') as f:
        f.write(xml)
    #~ Enviamos a timbrar
    pac = PAC(atributos['emisor']['rfc'])
    pac.xml_send = xml
    if pac.timbrar(id_cfdi):
        t = ET.fromstring(pac.xml)
        t = t.find('{}Complemento/{}TimbreFiscalDigital'.format(
            PREFIX[VERSION], PREFIX['TIMBRE']))
        name = 'timbradas/{}.xml'.format(t.attrib['UUID'])
        with open(name, 'w') as f:
            f.write(pac.xml)
        log.info('Factura timbrada correctamente: {}'.format(name))
    else:
        log.debug(pac.error)