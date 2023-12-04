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

`export PYTHONPATH=.

#export DB_URI=postgresql://admin:admin123@localhost:5432/test-back-posts3

`coverage run -m pytest`

`coverage report -m`

Si te esta fallando un test en particular, podes probar con:
`pytest -k "nombre_test" tests/*`

sudo lsof -i :<puerto>
sudo kill -9 pid


sudo chmod -R 777 .

docker exec -it postgres_taller2 psql -U admin -d postgres -c "CREATE DATABASE \"test-back-posts3\";"
