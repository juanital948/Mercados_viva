Mercado Viva - MVP

MVP para el proceso de compra digital de Mercado Viva, enfocado en resolver el problema de inventario que no coincide entre la tienda y los canales digitales (web/app), lo que hoy genera cancelaciones de pedidos después de confirmados.

Problema que resuelve

El inventario mostrado en línea no siempre coincide con el disponible en tienda. Este MVP valida el stock real antes de confirmar un pedido, reserva temporalmente el inventario mientras el cliente paga (evitando sobreventa) y sugiere una alternativa cuando no hay stock suficiente.

Objetivo: reducir en al menos 80% las cancelaciones de pedidos digitales por falta de inventario.

Flujo principal
Cliente agrega productos al carrito y confirma la compra.
El sistema valida disponibilidad real en la tienda asignada.
Si hay stock: se reserva por 10 minutos mientras se procesa el pago.
Si el pago no se completa en ese tiempo, la reserva se libera automáticamente.
Si no hay stock suficiente: se sugiere otra tienda con el mismo producto o un producto similar.
Al confirmarse el pago, se descuenta el inventario real y el pedido pasa a estado confirmado.
Arquitectura

Cliente / Operador
    ↓
Interfaz web (HTML/CSS/JS)
    ↓ JWT, HTTPS
Backend / API REST (Flask)
    ↓
Servicios: Inventario · Pedidos · Pagos · Clientes
    ↓
Base de datos: PostgreSQL (Neon)
    ↓
Operación: Tienda prepara → Domicilio entrega

Corresponde al diagrama de arquitectura del caso (draw.io), donde cada capa del backend está implementada como una sección dentro de app.py.

Tecnologías
Frontend: HTML, CSS, JavaScript
Backend: Python, Flask, Flask-JWT-Extended
Base de datos: PostgreSQL (Neon) / SQLite en local
Despliegue: Render (backend) + Vercel o Netlify (frontend)
Estructura del repo

Mercados_viva/
├── backend/
│  ├── app.py        # API REST + lógica de negocio (inventario, pedidos, pagos, clientes)
│  ├── requirements.txt
│  └── test_app.py    # pruebas automáticas
├── frontend/
│  └── index.html      # catálogo, carrito y checkout
└── README.md

Cómo correrlo en local
Backend
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

Por defecto usa SQLite. Para usar PostgreSQL (Neon), define la variable de entorno antes de correr:

export DATABASE_URL=postgresql://usuario:password@host/basedatos
Frontend

Abre frontend/index.html en el navegador (o con Live Server). Si el backend corre en otro puerto o está desplegado, actualiza la constante API al inicio del <script>.

Pruebas
cd backend
pytest

Incluye caso exitoso, caso de pago, y un caso excepcional (pedido con cantidad mayor al stock disponible).

API
Método	Ruta	Descripción
POST	/api/auth/login	Crea o autentica un cliente/operador, devuelve JWT
GET	/api/productos	Lista el catálogo con disponibilidad real
POST	/api/pedidos	Crea un pedido y reserva inventario (requiere JWT)
POST	/api/pedidos/<id>/pagar	Confirma el pago y descuenta inventario (requiere JWT)
PATCH	/api/pedidos/<id>/estado	Actualiza estado de preparación/entrega (solo rol operador)
Despliegue
Backend: Render → build pip install -r backend/requirements.txt, start cd backend && gunicorn app:app
Base de datos: Neon (PostgreSQL, capa gratuita)
Frontend: Vercel o Netlify apuntando a la carpeta frontend/
Restricciones del caso
No se puede detener la operación de las tiendas físicas: la validación de inventario se integra sobre el mismo dato de stock sin requerir cambios en el POS.
Presupuesto limitado: el MVP no implementa un sistema de inventario en tiempo real completamente nuevo, sino una capa de validación sobre el stock existente.
