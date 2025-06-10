# Nombres

Baccarini Camila
Cendoya Ramiro 
Vidmar Ian
Tassi Marcelo
Carini Matias
Mallqui Joe

# Eventhub

Aplicación web para venta de entradas utilizada en la cursada 2025 de Ingeniería y Calidad de Software. UTN-FRLP

## Dependencias

- python 3
- Django
- sqlite
- playwright
- ruff

## Instalar dependencias

`pip install -r requirements.txt`

## Setear variables de entorno
### Linux (bash): 
export DJANGO_SECRET_KEY=LLAVE_SECRETA
### Windows (cmd):
set DJANGO_SECRET_KEY=LLAVE_SECRETA

## Iniciar la Base de Datos

`python manage.py migrate`

### Crear usuario admin

`python manage.py createsuperuser`

### Llenar la base de datos

`python manage.py loaddata fixtures/events.json`

## Iniciar app

`python manage.py runserver`

# Docker

## Construir la imagen de docker
`docker build -t eventhub .`

## Correr la imagen (desarrollo)
docker run -it --env-file .env -p 8000:8000 eventhub

## Correr la imagen (produccion)
docker run -e DJANGO_SECRET_KEY="LLAVE_SECRETA" -e DJANGO_SETTINGS_MODULE=eventhub.settings -p 8000:8000 eventhub