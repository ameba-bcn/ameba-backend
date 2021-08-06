# ameba-site backend v0.21

### Release notes

#### 0.22
##### Features
- AW-216: added relevant info to member_profile


#### 0.21
##### Features
- AW-186: group is mandatory FK in models.Subscription

#### 0.20
##### Features
- AW-176: Cart state is a dictionary with computed-on-the-fly cart state
 attributes.
- AW-176: Cart state docs in GET /cart/current/
- AW-176: /api/member_register/ docs
- AW-176: /api/users/ with cart_id docs
- AW-177: email links to frontend with /ameba-site/ in url root

#### 0.19
##### Features
- AW-173: Cart now have state attribute with cart process state flow.
- AW-173: POST /api/users/ have optional attribute cart_id
- AW-173: POST /api/member_register/ have required attribute cart_id

##### Bugfixes
- AW-173: /api/docs/ not working due to wrong body_request on GET doc

#### 0.18
##### Features
- AW-171: General file instead of image for cover video
- AW-155: Endpoint /api/about/ for AMEBA's about info

##### Bugfixes
- AW-169 Activation email not sent on member+user registration

#### 0.17
##### Features
- Subscription creates member after pruchase

##### Bugfixes
- ```/api/subscriptions/ returned no data```
- Fixtures updated due to new db model

#### 0.16
##### Features
- Endpoints for member profile ```/api/users/<id>/member_profile/```
- User+Member register endpoint ```/api/member_register/```

##### Bugfixes
- ```/api/token/refresh/``` wrong routing expected password and username

#### 0.15
##### Features
- Images with 1x1 aspect
- Fixtures for new models (compatible with 0.14)
- Interview/Artist reworked

#### 0.14
##### Features
- ItemVariants model
- PATCH /api/cart/current/ con body `{'item_variant_ids': [id_1, id_2]}`
- Key variants con variants info e id en:
    ```
    /api/articles/
    /api/events/
    /api/subscriptions/
    ```
- Finalización de proceso de compra sin pasar por stripe cuando el precio total
 del carro es 0

#### 0.13
##### Features
- `/api/subscribe/` endpoint para subscripciones de email
- Funcionalidad "SUBSCRIBE" en emails apuntando a `/subscribe/?email=<email` (frontend)
- Signals de subscripción al registrar usuario, sincronización con MAILGUN
- Admin panel para mailing lists y subscribers

#### 0.12
##### Features
- Email confirmación de cuenta con tabla implementada
#### Bugfixes
- localhost harcoded en contenido de templates (urls rotas)
#### 0.11
##### Features
- Flujo de recuperación de cuenta en /api/recovery/
- Flujo de activación de cuenta en /api/activate/
- Visuales de portada en /api/covers/
- Envío de email de activación cuando usuario no activo intenta hacer login.
- Templates de email con diseños de Marc
- Fuentes de media de artistas en /api/artists/ y /api/artists/<artist-id>/
- Documentación mejorada para nuevos endpoints.
##### Bugfixes
- Link de activación mal formado en email de activación


#### 0.10
- Tests de proceso de pagos
- Fix  requirements

#### 0.9
- Bugfixes:
    - Problemas con el carro --> mensaje "Cart not processed"
- Test cases para carro
- Mejorado el flujo del carro

#### 0.8
- Pasarela de pagos implementada.
- Fixed: createsuperuser creaba usuarios inactivos.
- Documentación de carrtito de la compra en /api/docs/

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
#### Load dataset
Dataset inicial con datos reales:
```
python manage.py loaddata demo.json
```
#### Crear dataset a partir de datos actuales
```
python manage.py dumpdata --indent 2 > demo.json
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
