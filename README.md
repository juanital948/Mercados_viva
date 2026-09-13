# Mercado VIVA — MVP: Verificación de Inventario para Compras Digitales

Plataforma omnicanal desarrollada como Producto Mínimo Viable (MVP) para la cadena de supermercados **Mercado VIVA**, enfocada en resolver problemas de disponibilidad de inventario en tiempo real para transacciones digitales.

---

## 📌 Descripción del Proceso Seleccionado
**Proceso:** Verificación de inventario para compras digitales.
* **Problema que resuelve:** Evita ventas de productos agotados mediante validaciones en tiempo real de stock por sucursal, ofreciendo alternativas de compra en otras sedes si no hay disponibilidad en la seleccionada.
* **Actores:** 
  * *Cliente en línea:* Explora catálogos, gestiona su carrito y realiza compras digitales.
  * *Operador / Tienda:* Controla el inventario global y actualiza el estado logístico de los pedidos (Empacado, En Camino, Entregado).
* **Reglas de negocio:** 
  1. No se puede procesar un pedido si la cantidad solicitada supera el stock actual de la sede.
  2. Si un producto no tiene stock, el sistema debe informar y sugerir sedes alternativas.
  3. Al completar una compra exitosa, el stock se descuenta automáticamente de la base de datos de esa sede.

---

## 🛠️ Tecnologías Utilizadas
La solución utiliza herramientas de código abierto:
* **Frontend:** HTML5, CSS3 (Variables, Grid, Flexbox), JavaScript (Vanilla JS / Arquitectura modular).
* **Backend:** Python 3.x, Flask, Flask-SQLAlchemy, Gunicorn.
* **Base de datos:** SQLite (para entorno local y persistencia ligera compatible con despliegues).
* **Despliegue / Publicación:** Render / Gunicorn (con soporte para `Procfile`).

---

## 🚀 Instrucciones para Ejecutar el Proyecto Localmente

Sigue estos pasos en tu terminal para correr la aplicación en tu máquina:

### 1. Clonar el repositorio y navegar a la carpeta
```bash
git clone <URL-DE-TU-REPOSITORIO>
cd <NOMBRE-DE-LA-CARPETA>