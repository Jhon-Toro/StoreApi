# StoreApi

Este proyecto es el backend de una aplicación de comercio electrónico desarrollado con **Python** y **FastAPI**. Proporciona una API RESTful que permite la gestión de productos, categorías, usuarios, órdenes y reseñas. El backend se conecta con una base de datos relacional y maneja la lógica de negocio necesaria para el funcionamiento de la aplicación.

## Características

- **Gestión de productos:** CRUD completo para productos.
- **Gestión de categorías:** CRUD completo para categorías de productos.
- **Autenticación y autorización:** Registro, inicio de sesión y manejo de permisos de usuario.
- **Gestión de órdenes:** Creación y seguimiento de órdenes de compra.
- **Reseñas de productos:** Los usuarios pueden añadir y visualizar reseñas de productos.

## Tecnologías Utilizadas

- **Python:** Lenguaje de programación principal.
- **FastAPI:** Framework para la construcción de APIs rápidas y eficientes.
- **Uvicorn:** Servidor ASGI para ejecutar la aplicación FastAPI.
- **Base de datos:** Se utiliza una base de datos relacional para almacenar la información.

## Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/Jhon-Toro/StoreApi.git

2. Navega al directorio del proyecto::

   ```bash
   cd StoreApi
   
3. Crea y activa un entorno virtual (opcional pero recomendado)::

   ```bash
   python -m venv modules
   source modulesv/bin/activate  # En Windows: modules\Scripts\activate

4. Instala las dependencias::

   ```bash
   pip install -r requirements.txt

5. Ejecución:
   ```bash
   uvicorn main:app --reload
   La API estará disponible en http://localhost:8000

## Documentación
FastAPI genera automáticamente documentación interactiva para la API:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
 
## Configuración
Asegúrate de configurar las variables de entorno necesarias para la conexión a la base de datos y otras configuraciones sensibles. Esto incluye:

- Conexión a la base de datos.
- Credenciales de API externas, como PayPal.
  
## Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para discutir cambios o mejoras.

## Licencia
Este proyecto está bajo la licencia MIT.

// API POSTMAN REST CLIENT

### Variables
@baseUrl = http://localhost:8000
@token = <your_actual_token>

### Register
POST {{baseUrl}}/auth/register
Content-Type: application/json

{
  "username": "David Toro2",
  "email": "toromurieljhon2@gmail.com",
  "password": "Test"
}

### Login
POST {{baseUrl}}/auth/login
Content-Type: application/json

{
  "email": "admin@gmail.com",
  "password": "adminpassword"
}

### Create Product
POST {{baseUrl}}/products/
Content-Type: application/json
Authorization: Bearer {{token}}

{
    "title": "Hola",
    "description": "Nueva descripción",
    "category_id": 6,
    "price": 19.99,
    "images": ["https://www.corbataslester.com/magazine/wp-content/uploads/2018/01/oxford02.jpg", "https://mariohernandez.vtexassets.com/arquivos/ids/213954/zapatos-garcia-negro-premium_1.jpg", ""]
}

### Delete Product
DELETE {{baseUrl}}/products/2
Authorization: Bearer {{token}}

### Edit Product
PUT {{baseUrl}}/products/2
Content-Type: application/json
Authorization: Bearer {{token}}

{
    "title": "Nuevo título actualizado",
    "description": "Descripción actualizada",
    "price": 25.99,
    "category_id": 5,
    "images": ["https://newimage1.jpg", "https://newimage2.jpg", ""]
}

### Get Product by ID
GET {{baseUrl}}/products/4
Authorization: Bearer {{token}}

### Get My Personal Orders
GET {{baseUrl}}/my_orders/
Authorization: Bearer {{token}}

### Get All Orders
GET {{baseUrl}}/orders/
Authorization: Bearer {{token}}

### Create Order
POST {{baseUrl}}/orders/
Content-Type: application/json
Authorization: Bearer {{token}}

{
  "total_price": 59.97,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 3,
      "quantity": 1
    }
  ]
}

### Create Review
POST {{baseUrl}}/reviews/
Content-Type: application/json
Authorization: Bearer {{token}}

{
    "rating": 5,
    "comment": "Excelente producto",
    "product_id": 2
}

### Get Category by ID
GET {{baseUrl}}/categories/4

### Delete Category
DELETE {{baseUrl}}/categories/10
Authorization: Bearer {{token}}

### Get All Categories
GET {{baseUrl}}/categories/

