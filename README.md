# 🛒 Mercado Viva - MVP

MVP para el proceso de compra digital de Mercado Viva, enfocado en resolver el problema de inventario que no coincide entre la tienda y los canales digitales (web/app), lo que hoy genera cancelaciones de pedidos después de confirmados.

---

## 📋 Tabla de Contenidos
1. [Problema que Resuelve](#-problema-que-resuelve)
2. [Flujo Principal](#-flujo-principal)
3. [Arquitectura](#-arquitectura)
4. [Tecnologías](#-tecnologías)
5. [Estructura del Repo](#-estructura-del-repo)
6. [Cómo Correrlo en Local (Windows y macOS)](#-cómo-correrlo-en-local-windows-y-macos)
7. [API](#-api)
8. [Despliegue](#-despliegue)
9. [Restricciones del Caso](#-restricciones-del-caso)
10. [Integrantes](#-integrantes)

---

## 📌 Problema que Resuelve

El inventario mostrado en línea no siempre coincide con el disponible en tienda. Este MVP valida el stock real antes de confirmar un pedido, reserva temporalmente el inventario mientras el cliente paga (evitando sobreventa) y sugiere una alternativa cuando no hay stock suficiente.

**Objetivo:** Reducir en al menos 80% las cancelaciones de pedidos digitales por falta de inventario.

---

## 🔄 Flujo Principal

1. Cliente agrega productos al carrito y confirma la compra.
2. El sistema valida disponibilidad real en la tienda asignada.
3. Si hay stock: se reserva por 10 minutos mientras se procesa el pago.
4. Si el pago no se completa en ese tiempo, la reserva se libera automáticamente.
5. Si no hay stock suficiente: se sugiere otra tienda con el mismo producto o un producto similar.
6. Al confirmarse el pago, se descuenta el inventario real y el pedido pasa a estado `confirmado`.

---

## 🏛️ Arquitectura

```text
Cliente / Operador
        │
Interfaz web (HTML/CSS/JS)
        │  JWT, HTTPS
Backend / API REST (Flask)
        │
Servicios: Inventario - Pedidos - Pagos - Clientes
        │
Base de datos: PostgreSQL (Neon) / SQLite en local
        │
Operación: Tienda prepara -> Domicilio entrega


🛠️ Tecnologías
Frontend: HTML, CSS, JavaScript

Backend: Python, Flask, Flask-JWT-Extended

Base de datos: PostgreSQL (Neon) / SQLite en local

Despliegue: Render (backend) + Vercel o Netlify (frontend)

📁 Estructura del Repo

mercado-viva/
├── backend/
│   ├── __pycache__/
│   ├── app.py             # API REST + lógica de negocio (inventario, pedidos, pagos, clientes)
│   └── database.py        # Modelos ORM y gestión de base de datos
├── frontend/
│   ├── css/
│   │   └── styles.css     # Estilos de la interfaz
│   ├── js/
│   │   └── app.js         # Lógica frontend, consumo de API
│   └── index.html         # Catálogo, carrito y checkout
├── mercado_viva.db        # Base de datos SQLite local
├── Procfile               # Configuración de despliegue WSGI (Gunicorn)
├── README.md              # Documentación oficial del proyecto
├── requirements.txt       # Dependencias de Python
└── test_app.py            # Pruebas automáticas


⚙️ Cómo Correrlo en Local (Windows y macOS)
🖥️ 1. Configuración y Ejecución del Backend
Abre tu terminal (CMD, PowerShell o Terminal de macOS) y ejecuta los siguientes comandos según tu sistema operativo:

Para macOS / Linux:

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python app.py

Para Windows (CMD o PowerShell):

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements.txt
python app.py


macOS/Linux: export DATABASE_URL=postgresql://usuario:password@host/basedatos

Windows (CMD): set DATABASE_URL=postgresql://usuario:password@host/basedatos


🌐 2. Ejecución del Frontend
Abre el archivo frontend/index.html directamente en tu navegador web o utilízalo con la extensión Live Server de Visual Studio Code. Si el backend corre en un puerto diferente o está desplegado, asegúrate de actualizar la constante API al inicio del script en el frontend.

🧪 3. Ejecución de Pruebas Automáticas (pytest)
Para verificar el correcto funcionamiento, ejecuta las pruebas automáticas en la carpeta raíz o backend:

pytest test_app.py -v

Incluye caso exitoso, caso de pago, y un caso excepcional (pedido con cantidad mayor al stock disponible).


Método,Ruta,Descripción
POST,/api/auth/login,"Crea o autentica un cliente/operador, devuelve JWT"
GET,/api/productos,Lista el catálogo con disponibilidad real
POST,/api/pedidos,Crea un pedido y reserva inventario (requiere JWT)
POST,/api/pedidos/<id>/pagar,Confirma el pago y descuenta inventario (requiere JWT)
PATCH,/api/pedidos/<id>/estado,Actualiza estado de preparación/entrega (solo rol operador)


🌐 Despliegue
Backend: Render → build pip install -r requirements.txt, start cd backend && gunicorn app:app

Base de datos: Neon (PostgreSQL, capa gratuita)

Frontend: Vercel o Netlify apuntando a la carpeta frontend/

⚠️ Restricciones del Caso
No se puede detener la operación de las tiendas físicas: la validación de inventario se integra sobre el mismo dato de stock sin requerir cambios en el POS.

Presupuesto limitado: el MVP no implementa un sistema de inventario en tiempo real completamente nuevo, sino una capa de validación sobre el stock existente.

👥 Integrantes
Valentina Sierra Ospina
Juanita Legarda
