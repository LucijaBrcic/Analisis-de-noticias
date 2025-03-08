# Analisis de noticias

## Estructura de carpetas y ficheros
- src (alojara todo el codigo fuente)
  - csv (alojaran ficheros csv)
  - model (alojaran ficheros que representas clases)
  - scraper (alojara codigo relacionado con el scraper)
  - streamlit_web (ficheros relacionados con la web hecha en streamlit)
    - app.py (punto de entrada de la web)
- requirements.txt (fichero de dependencias)
- .gitignore (fichero donde se listan ficheros a ignorar en git)
- README.md (fichero README de instrucciones)

## Setup & Instalación
- Crear un entorno virtual dedicado (virtualenv)
- Instalar dependencias (requirements.txt)

### Crear un entorno virtual
Se puede crear de distintas maneras, con conda, con virtualenv.

Aqui explicamos como crearlo con el modulo venv de python

- python3 -m venv entorno_virtual

Nota: si en la instalacion diera error el modulo venv, 

es porque no existe python3-venv

instalar python3-venv (si no lo tuvieramos) (depende de cada sistema operativo)

### Como activar un entorno virtual
- Linux & Mac: 
  - source entorno_virtual/bin/active
- Windows:
  - .\entorno_virtual\Scripts\activate

### Instalación de las dependencias (una vez activdo el entorno)

Este comando instala todas las dependencias incluidas en el fichero requirements.txt

`pip install -r requirements.txt`

### Ejecutar Web
`streamlit run src/streamlit_web/app.py`

### Autores
- Lucia
- Jordi
- Luis
