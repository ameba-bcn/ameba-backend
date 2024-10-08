### Release notes

### 1.43
- Implementado member profile con imagenes y tags
- Implementado EP `GET /api/genres/` con los géneros disponibles
- Implementado EP `/api/profile_images/` para borrar imagenes de perfil


### 1.42
- AW-497: implemented member profile project attributes and member_projects lists.


### 1.41
- fix: removed pick-up message from payment emails when there aren't articles (AW-443)


### 1.40
- fix: ordering questions (AW-466)
- fix: search bar in members admin view broken (AW-487)
- Added collaborators list endpoint to api and admin (AW-478)
- Added maps_url field to events detail api (AW-435)
- Added created field to artists list and detail api (AW-479)

### 1.31
- fix: dependencies
- Admin events with participant lists
- Admin event list with participant number
- Admin members with filters (type, status)

### 1.29
- AW-459: "bug" reintroduced not to break functionality

### 1.28
- Hotfix: try except clause for delete previous subscriptions
- AW-455: Added benefits to subscriptions list
- AW-452: Sorting Interview questions by Question.position
- AW-440: Add creation date to artist profile and sort by it
- AW-441: Added item_type to cart items

### 1.27
- Removed url from artist media field

### 1.26
- Added offset to initial member number

#### 1.25
- Replaced ameba-site from all urls

#### 1.24.1
- Added url to admin panel in artist media field

#### 1.24
- AW-423: Added expire time according to item_variant period
- AW-421: Added CORS headers

#### 1.23
- AW-403: Added embedded field to artist media

#### 1.22
- AW-401: Added order date sort by articles

#### 1.21
- AW-400: Added items to emails after subscription renew 
- AW-394: Modified QR system to work with APP

#### 1.20
- AW-390: variant details to json and added item name in cart
- AW-393: set customer's default payment method after every payment.
- AW-391: add header to event model, serializer and admin panel translated.
- AW-358: renamed about to manifest

#### 1.19.1
- bugfix: compras no funcionan (setup_future_usage accedía a payment intent 
  antes de cerrar invoice)

#### 1.19
- AW-375: bugfix -> compras stripe rotas (setup_future_usage mal actualizado)

#### 1.18
- AW-372: bugfix -> no se recibe email de confirmacion de subscripcion a 
  newsletters.
- AW-371: bugfix -> pagos periodicos no funcionan para subscripciones 
  (setup_future_usage en stripe)


#### 1.17
- AW-368: Remove recurrence options from non-subscriptions in admin panel

#### 1.16
- AW-356: increased length of interview description and answers to 5000
- AW-363: increased length of item description to 5000
- AW-361: added artist_id to interviews and interview

#### 1.15
- Fixed deps

#### 1.14
- AW-355: Fixing qr local files in prod

#### 1.13
- AW-352: Added orders section in admin panel

#### 1.12
- AW-351: added api_public to api/carts/current/payments

#### 1.11
- AW-347: Emails updated with new texts

#### 1.10
- AW-346: Improved column selection colors in admin panel
- AW-346: Added favicon to admin panel
- AW-342: Fixed search in admin cart menu

#### 1.9
- Added new admin look and feel
- AW-340: Erro al crear un usuario nuevo -> Importante añadir 
  EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend" en .env para 
  entornos locales.

#### 1.8.1
- AW-333: bugfix - Payment.status read on the fly from stripe caused problems
- AW-338: bugfix - Coupon 0 is not allowed in stripe

#### 1.8
- AW-335: Discounts integration with stripe

#### 1.7
- AW-327: Implemented member profile cards from stripe
- AW-304: Check already active subscription in cart checkout
- AW-334: Failed payments stripe webhook handling
- AW-329: Preguntas y respuestas de entrevistas ampliadas a 2000 caracteres.

#### 1.6
- AW-331: implementado stripe webhook handling para evento invoice.
  paymen_succeeded.

#### 1.5.1
- hotfix: psycopg2-binary last version broken: fixed to 2.8


#### 1.5
- AW-319: Changed payment flow to work with PaymentIntent and new payments 
  form.

#### 1.4
- AW-232: Implemented new payment flow to enable periodic charges for 
  subscriptions


#### 1.3
- AW-290: added embedded field to artist media url
- AW-279: added DNI to member profile
- AW-294: Improved payment email
- AW-295: Added event email confirmation
- AW-297: Added email soci-pro
- AW-298: added email auto-renew notification
- AW-299: added member card with QR
- AW-300: added evnt tickets with QR
- AW-301: added auto-renewal email confirmation
- AW-302: added unable to renew notification
- AW-303: added email backgroun and width


#### 1.2
##### Features
- AW-266: Added featured field to artists
- AW-267: Added is_subscription field to cart items 
- AW-270: Added variant_details field to cart items
- AW-268: Subscriptions history on member_profile checked

##### Bugfixes
- AW-272: Solved security deps warnings
- AW-269: Backend served files with abs url and http protocol
- AW-270: Item variant names in cart appeared as ItemVariant(item='item_name')

#### 1.1
##### Features
- AW-231: Added has_interview and is_ameba_dj tags to artists.
- AW-259: Removed english language from site

##### Bugfixes
- AW-217: Missing purchased by artist Event information
- AW-230: Email case sensitive


#### 1.0
##### Features
- AW-228: copy translations for admin panel to spanish and english
- AW-227: customised admin panel
- AW-226: added tags to artists
- AW-205: added event type to event models
- AW-220: added dynamic localization via Accept-Language header (es/ca/en)
- AW-220: editable user's preferred language (PATCH /api/users/current/) 

##### Bugfixes
- AW-220: User email and password can not be updated anymore.

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
