# ameba backend v1.5

## Requisitos
- Docker

## Desarrollo Dockerizado en VSCode
- Mac: `cmd + shift + P` -> ">Dev Containers: Rebuild and Reopen in Container"
- Windows: `ctrl + shift + P` -> ">Dev Containers: Rebuild and Reopen in Container"

Esto levantará una instancia de VSCode remota dentro del propio container de desarrollo que permite debuguear usando checkpoints con mayor facilidad.

## REST-API

### Ejecutar tests
```
docker compose run --rm ameba-backend python manage.py test
```

### Migraciones
- Aplicar migraciones
```
docker compose run --rm ameba-backend python manage.py migrate
```

- Generar nuevas migraciones en modelos
```
docker compose run --rm ameba-backend python manage.py makemigrations
```

### Compilar copies
```
docker compose run --rm ameba-backend python manage.py compilemessages
```

### Generar static assets del admin
```
docker compose run --rm ameba-backend python manage.py collectstatic
```

### Levantar backend
```
docker compose up
```

### Demo data
#### Load dataset
Dataset inicial con datos reales:
```
docker compose run --rm ameba-backend python manage.py loadlocal
```
#### Crear dataset a partir de datos actuales
```python
docker compose run --rm ameba-backend python manage.py dumpdata --indent 2 > demo.json
```

#### Cargar dataset creado
```python
docker compose run --rm ameba-backend python manage.py loaddata demo.json
```

### Localización
La localización depende únicamente del cliente, aunque se puede guardar un 
lenguage preferido en ```/api/users/current/```

El lenguage preferido se puede cambiar haciendo un PATCH e indicando el 
código de lenguage "es" (español), "ca" (catalán) o "en" (inglés):
```
PATCH /api/users/current/ 
--form "language": "es"
```

Para consultar el lenguage preferido por el usuario si lo hubiese:
```
GET /api/users/current/
```

### Documentación
Documentación SWAGGER de la API:
```
localhost:8000/api/docs
```

### Admin panel
```
localhost:8000/admin
```
Para acceder al admin panel hay que tener un usuario admin. Para ello, desde
 django:
```
docker compose run --rm ameba-backend python manage.py createsuperuser
```

### Authentication
El método de authenticación es json-web-token (JWT) implementado por: 
[DRF-SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)

Pasos para autenticar:
- POST request con la siguiente estructura:
```
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "whateveruser", "password": "whateverpassword"}' \
  http://<ameba-site>:8000/api/token/

Response:
{
  "access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU",
  "refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"
}
```
- Almacenar access y refresh token en el browser local storage.
- Usar el **access** token en todas las siguientes requests, como
"Authorization" header:
```
curl \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU" \
  http://localhost:8000/api/some-protected-view/
```
- Cuando **access** token expira, se usa el refresh token para obtener un
 nuevo access token:
```
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"}' \
  http://localhost:8000/api/token/refresh/

Response:
{"access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNTY3LCJqdGkiOiJjNzE4ZTVkNjgzZWQ0NTQyYTU0NWJkM2VmMGI0ZGQ0ZSJ9.ekxRxgb9OKmHkfy-zs1Ro_xs1eMLXiR17dIDBVxeT-w"}
```
