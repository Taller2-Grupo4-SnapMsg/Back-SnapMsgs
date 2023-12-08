# Back-SnapMsgs
Código de backend para los tweets (snapmsgs) y todo lo relacionado a ellos (likearlos, compartirlos, etc)

# Antes de ejecutar

#### Exportar las URIs

```bash
export DB_URI=postgresql://cwfvbvxl:jtsNDRjbVqGeBgYcYvxGps3LLlX_t-P5@berry.db.elephantsql.com:5432/cwfvbvxl
```

## Para levantar una nueva tabla

```bash
alembic -c repository/alembic.ini revision --autogenerate -m "mi_comentario"
```

```bash
alembic -c repository/alembic.ini  upgrade head
```

## Para instalar todos los requirements

```bash
pip install -r requirements.txt
```

ó

```bash
pip3 install -r requirements.txt
```

## Para correr pylint

```bash
find . -type f -name "*.py" | xargs pylint
```

## Para correr los tests locales

*Crear base de datos local*
1- Cuando esta corriendo el doker ejecutar:

```bash
docker exec -it postgres_taller2 psql -U admin -d postgres -c "CREATE DATABASE \"test-back-users\";"
```

2- Frenar el docker y volver a correrlo con la base de datos ya creada

```bash
export PYTHONPATH=.
```

```bash
export DB_URI=postgresql://admin:admin123@localhost:5432/test-back-users
```

```bash
coverage run -m pytest
```

*Para obtener el reporte de coverange*

```bash
coverage report -m --omit "/usr/*"
```

*Para correr un test en particular*

```bash
pytest -k "test_delete_all" tests/*
```

*Si necesitas dar permisos a la carpeta de data de postgres*

```bash
sudo chmod -R 777 .
```

### Si ya tenias algo corriendo en ese puerto, lo podes eliminar con

```bash
sudo lsof -i :<puerto>
sudo kill -9 <pid_del_proceso>
```