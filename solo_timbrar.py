import logging
import os
import sys
from xml.etree import ElementTree as ET
import datetime
import time
from pyPAC import ECODEX as PAC
from settings import DEBUG, LOG, PREFIX


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


def get_epoch(date):
    e = int(time.mktime(date.timetuple()))
    return e


if __name__ == '__main__':
    path_xml = sys.argv[1]

    if not os.path.exists('timbradas'):
        os.mkdir('timbradas')
    if not os.path.exists(path_xml):
        sys.exit(0)

    now = datetime.datetime.now()
    id_cfdi = get_epoch(now)
    xml = ET.parse(path_xml).getroot()
    version = xml.attrib['version']
    emisor = xml.find('{}Emisor'.format(PREFIX[version]))
    #~ Enviamos a timbrar
    pac = PAC(emisor.attrib['rfc'])
    pac.xml_send = open(path_xml, 'r').read()
    if pac.timbrar(id_cfdi):
        t = ET.fromstring(pac.xml)
        t = t.find('{}Complemento/{}TimbreFiscalDigital'.format(
            PREFIX[version], PREFIX['TIMBRE']))
        name = 'timbradas/{}.xml'.format(t.attrib['UUID'])
        with open(name, 'w') as f:
            f.write(pac.xml)
        log.info('Factura timbrada correctamente: {}'.format(name))
    else:
        log.debug(pac.error)