# Back-SnapMsgs
Código de backend para los tweets (snapmsgs) y todo lo relacionado a ellos (likearlos, compartirlos, etc)

# Antes de ejecutar

#### Exportar las URIs

`export DB_URI=postgresql://cwfvbvxl:jtsNDRjbVqGeBgYcYvxGps3LLlX_t-P5@berry.db.elephantsql.com:5432/cwfvbvxl`


# Para levantar una nueva tabla

```
alembic -c repository/alembic.ini revision --autogenerate -m "mi_comentario"
```

```
alembic -c repository/alembic.ini  upgrade head
```


# Para instalar todos los requirements
```
pip install -r requirements.txt
```

ó

```
pip3 install -r requirements.txt
```

# Para correr pylint
```
find . -type f -name "*.py" | xargs pylint
```

# Si hay permisos denegados
en la parte de data, skipealos de esta manera:
```
sudo chmod -R 755 data/postgres/
```