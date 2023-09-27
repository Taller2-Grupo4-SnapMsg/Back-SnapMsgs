# Back-SnapMsgs
Código de backend para los tweets (snapmsgs) y todo lo relacionado a ellos (likearlos, compartirlos, etc)



# Antes de ejecutar

#### Exportar las URIs

`export DB_URI=postgres://exoiymmb:4HyrnUG6vFsTwmhIG_B_N6j2NdyKMt5s@motty.db.elephantsql.com:5432/exoiymmb`

`export DB_USERS_URI="postgresql://cwfvbvxl:jtsNDRjbVqGeBgYcYvxGps3LLlX_t-P5@berry.db.elephantsql.com:5432/cwfvbvxl"`


# Para levantar una nueva tabla

```
alembic revision --autogenerate -m "motivo de la migración"
```


# Para instalar todos los requirements
```
pip install -r requirements.txt
```

ó

```
pip3 install -r requirements.txt
```