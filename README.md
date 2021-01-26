# ameba-site backend v0.6

### Release notes

#### 0.7
- Current tag para acceder al carro del usuario
    - (GET,PATCH) /api/carts/current/
- Cambio de Article.variants a Article.sizes 
- Subscriptions(Item):
    - (GET) /api/subscriptions/
    - (GET) /api/subscriptions/<id>/
- Implementado nuevo logout:
    - (DELETE) /api/token/<refresh-token>/

#### 0.6
- Implementados eventos y saved events:
    - /api/events/
    - /api/events/{pk}/
    - /api/users/current/events/saved/
- Implementados favoritos.
- Añadidas fixtures de eventos y admin panel.
#### 0.5
- Implementada la botiga:
    - /api/articles/
    - /api/articles/{pk}/
- Renamed artist to interviews
- Admin panel mejorado
- +Testcases

#### 0.4
- Documentación en /api/docs/
- Demo data con loaddata demo.json (comando abajo y en devops)
- Tests
- login/logout
- support-your-locals

## REST-API

### Ejecutar tests
```
python manage.py test
```

### Ejecutar RestApi
Para poner en marcha la API, ejecutar al menos una vez:
```
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

### Demo data
Dataset inicial con datos reales:
```
python manage.py loaddata demo.json
```

### Documentación
Documentación SWAGGER de la API:
```
localshot:8000/api/docs
```

### Admin panel
```
localhost:8000/admin
```
Para acceder al admin panel hay que tener un usuario admin. Para ello, desde
 django:
```
python manage.py createsuperuser
```
o desde docker:
```
docker-compose run --rm backend python manage.py createsuperuser
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
