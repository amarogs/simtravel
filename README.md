# simtravel
Simulador de tráfico urbano mediante un modelo híbrido AC-autómata. 
Es un simulador de tráfico en el que creamos ciudades sintéticas y simétricas y colocamos vehículos que pueden ser eléctricos y no eléctricos. 
Además permite el estudio de la colocación de estaciones de recarga probando con 3 tipos de colocaciones.
* Una estación grande en el centro.
* Cuatro estaciones medianas distribuidas por la ciudad.
* Múltiples estaciones pequeñas repartidas de manera homogénea.

Los archivos binarios con la aplicación empaquetada se pueden descargar de:



### Requisitos previos
Tener instalado Python 3 (probado en la versión 3.8),  tener instalado el gestor de paquetes pip y tener instaladas las dependencias para
poder compilar extensiones.

```
apt-get install python3
apt-get install python3-pip
apt-get install python3-dev
```

### Instalación
Pimero creamos el entorno virtual de Python 

```
pip3 install virtualenv
python3 -m virtualenv simtravel-env
source simtravel-env/bin/activate
```
Ahora instalamos los módulos que necesitamos y compilamos el código como extensiones de Python.
```
pip3 install -r requirements.txt
python3 setup.py build_ext --inplace
```

### Ejecución
Para ejecutar la aplicación de escritorio lanzamos el archivo de run_app.py que se encuentra en la carpeta scripts.

```
python3 -m scripts.run_app
```

Para ejecutar el script paralelo debemos modificar los parámetros que se encuentran en la carpeta scripts/parameters.yml y ejecutar el siguiente comando donde -np es el número de procesos que queremos utilizar y con -pf indicamos la ruta al archivo de parámetros. Si no se suministra -np se usará 1 proceso y si no se suministra -pf se buscará el archiov de parámeotros de la carpeta scripts.

```
python3 -m scripts.run -np 16 -pf /home/amaro/parameters.yaml
```
