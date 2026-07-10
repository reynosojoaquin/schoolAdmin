# SchoolAdminLitePy

Sistema escolar liviano inspirado en `SchoolControlApp`, reescrito en Python con Django.

## Objetivo

Mantener una base simple y lista para servidor Linux:

- Django como framework principal.
- PostgreSQL en contenedor.
- SQLite opcional para desarrollo local rapido.
- Bootstrap ligero para la interfaz.
- Gunicorn + Nginx en Docker para despliegue.

## Estructura

```text
SchoolAdminLitePy/
  manage.py
  requirements.txt
  Dockerfile
  docker-compose.yml
  .env.example
  .env.docker.example
  schooladminlite/
  apps/
    core/
      models.py
      admin.py
      views.py
      urls.py
  docker/
    entrypoint.sh
    nginx/
  templates/
  static/
```

## Uso con Docker

Este es el flujo recomendado para desarrollo y despliegue.

```bash
cd SchoolAdminLitePy
cp .env.docker.example .env
docker compose up --build
```

La aplicacion queda disponible en:

```text
http://localhost:8025
```

Crear usuario administrador:

```bash
docker compose exec web python manage.py createsuperuser
```

Detener los contenedores:

```bash
docker compose down
```

Detener y borrar tambien la base de datos local:

```bash
docker compose down -v
```

## Docker con Nginx

Para levantar app, PostgreSQL y Nginx:

```bash
docker compose --profile production up --build
```

La aplicacion queda disponible en:

```text
http://localhost:8026
```

## Instalacion local

```bash
cd SchoolAdminLitePy
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

En Windows PowerShell:

```powershell
cd SchoolAdminLitePy
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Modulos iniciales

- Provincias, ciudades y sectores.
- Nacionalidades y lugares de nacimiento.
- Cursos.
- Asignaturas.
- Competencias por asignatura.
- Estudiantes.
- Docentes.
- Empleados administrativos.
- Direcciones, telefonos y contactos.
- Inscripciones.
- Calificaciones.
- Curriculum de docentes y empleados.

La estructura toma como referencia las clases del proyecto `.NET`, pero con estas mejoras:

- Campos personales comunes reutilizados para estudiantes, docentes y empleados.
- Direcciones, telefonos y contactos relacionados directamente con la persona correspondiente.
- Calificaciones vinculadas a inscripcion, asignatura y opcionalmente competencia.
- Catalogos separados para tipos de direccion, telefono, contacto, empleado y curriculum.

## Produccion Linux

Variables recomendadas:

```bash
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=midominio.com,www.midominio.com
DATABASE_URL=postgres://usuario:clave@localhost:5432/school_admin_lite
```

Con Docker, el despliegue minimo en Linux es:

```bash
cp .env.docker.example .env
nano .env
docker compose --profile production up -d --build
```

El contenedor `web` ejecuta automaticamente:

- Migraciones de base de datos.
- Recoleccion de archivos estaticos.
- Gunicorn como servidor de aplicacion.
