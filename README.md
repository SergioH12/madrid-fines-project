# madridFines

`madridFines` es un paquete que permite **descargar, analizar y visualizar datos de multas de circulación de la ciudad de Madrid**, directamente desde el portal de datos abiertos del Ayuntamiento.

El objetivo es facilitar el análisis de las infracciones, su clasificación y la recaudación total o por tipo de multa, todo ello con un sistema de **caché inteligente** que evita descargas repetitivas.

---

## Instalación del paquete

1. generar el archivo `.whl` con el comando `python -m build`.

2. Instalar el paquete con el siguiente comando (desde el directorio donde se encuentra el archivo):

```bash
pip install madridFines-1.0.0-py3-none-any.whl
````

>  Asegúrese de tener Python 3.10 o superior y `pip` actualizado.
> Se recomienda hacerlo en un ambiente virtual de python `venv`

---

##  Estructura del proyecto

```
madridFines/
├── __init__.py
├── cache.py           # Manejo de caché en disco
├── cacheUrl.py        # Descarga y almacenamiento temporal de URLs
├── madridFines.py     # Lógica principal de descarga y análisis
tests/
├── data/
│   ├── multas_sample.csv
│   └── test_page.html
├── test_madridFines.py
├── test_cache.py
├─── test_cacheurl.py
notebooks/
├──Etapa1.ipynb
└──validacion_clases.ipynb
```

---
##  Uso básico del módulo

Una vez instalado, se puede importar y utilizar el paquete, dentro de la carpeta "notebooks" existe un fichero llamado
validacion_clases.ipynb, que contiene algunos ejemplos de uso de los metodos de cada clase

