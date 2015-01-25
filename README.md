cfdi-test te muestra el proceso de creación, sellado y timbrado de facturas
electrónicas (CFDIs) para México usando Python.

Tenemos un script para crear, sellar y timbrar un CFDI mínimo.

    python3 sellar_timbrar.py

Y otro para solo enviar a timbrar, por si quieres validar que tus CFDIs estan
bien generados.

    python3 solo_timbrar.py fac_temp.xml

Consulta el [wiki](https://github.com/mauriciobaeza/cfdi-test/wiki) para más
información.