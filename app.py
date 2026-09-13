import os
import uuid
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from backend.database import db, init_db, Sede, Producto, Pedido

# Como app.py ya está en la raíz, el directorio base es el actual:
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=FRONTEND_DIR, static_url_path='')
# Habilita peticiones CORS desde Live Server o cualquier cliente frontend
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'mercado_viva.db')}")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

class ServicioInventario:
    @staticmethod
    def validar_stock(sede_id, items):
        for item in items:
            prod = Producto.query.filter_by(id=item['id'], sede_id=sede_id).first()
            if not prod or prod.stock < item['cantidad']:
                alternativas = db.session.query(Sede.nombre).join(Producto).\
                    filter(Producto.nombre == item['nombre'], Producto.stock >= item['cantidad'], Sede.id != sede_id).all()
                nombres_sedes = [alt[0] for alt in alternativas]
                return False, f"Stock insuficiente para '{item['nombre']}'.", nombres_sedes
        return True, "Stock disponible.", []

    @staticmethod
    def descontar_stock(sede_id, items):
        for item in items:
            prod = Producto.query.filter_by(id=item['id'], sede_id=sede_id).first()
            if prod:
                prod.stock -= item['cantidad']
        db.session.commit()

class ServicioPagos:
    @staticmethod
    def procesar_pago(metodo, monto):
        if not metodo or monto <= 0:
            return False, "Método de pago o monto inválido."
        return True, "Pago procesado exitosamente."

# ==========================================
# ENDPOINTS API REST
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sedes', methods=['GET'])
def get_sedes():
    sedes = Sede.query.all()
    return jsonify({"exito": True, "sedes": [{"id": s.id, "nombre": s.nombre} for s in sedes]})

@app.route('/api/sedes/<sede_id>/catalogo', methods=['GET'])
def get_catalogo(sede_id):
    productos = Producto.query.filter_by(sede_id=sede_id).all()
    return jsonify({
        "exito": True, 
        "productos": [{"id": p.id, "nombre": p.nombre, "precio": p.precio, "stock": p.stock} for p in productos]
    })

@app.route('/api/inventario-global', methods=['GET'])
def get_inventario_global():
    sedes = Sede.query.all()
    resultado = []
    for s in sedes:
        prods = Producto.query.filter_by(sede_id=s.id).all()
        resultado.append({
            "sede": s.nombre,
            "productos": [{"id": p.id, "nombre": p.nombre, "stock": p.stock, "precio": p.precio} for p in prods]
        })
    return jsonify({"exito": True, "inventario": resultado})

@app.route('/api/pedidos/crear', methods=['POST'])
def crear_pedido():
    data = request.get_json() or {}
    cliente = data.get('cliente', {})
    items = data.get('items', [])
    sede_id = data.get('sede_id')
    metodo_pago = data.get('metodo_pago')

    if not cliente.get('nombre') or not cliente.get('email') or not cliente.get('direccion'):
        return jsonify({"exito": False, "mensaje": "Datos del cliente incompletos."}), 400
    
    if not items:
        return jsonify({"exito": False, "mensaje": "El carrito está vacío."}), 400

    valido, msg, alternas = ServicioInventario.validar_stock(sede_id, items)
    if not valido:
        sug = f"Disponible en: {', '.join(alternas)}" if alternas else "Agotado en todas las sedes."
        return jsonify({"exito": False, "mensaje": msg, "sugerencia": sug}), 400

    total = sum(item['precio'] * item['cantidad'] for item in items)

    pago_ok, msg_pago = ServicioPagos.procesar_pago(metodo_pago, total)
    if not pago_ok:
        return jsonify({"exito": False, "mensaje": msg_pago}), 400

    ServicioInventario.descontar_stock(sede_id, items)
    
    nuevo_pedido = Pedido(
        id=f"ORD-{uuid.uuid4().hex[:6].upper()}",
        cliente_nombre=cliente['nombre'],
        cliente_email=cliente['email'],
        direccion=cliente['direccion'],
        sede_id=sede_id,
        total=total,
        estado="Preparando en Tienda",
        metodo_pago=metodo_pago,
        pagado=True
    )
    db.session.add(nuevo_pedido)
    db.session.commit()

    return jsonify({
        "exito": True,
        "orden_id": nuevo_pedido.id,
        "mensaje": "Pedido registrado y enviado a la Tienda para empaque."
    }), 201

@app.route('/api/pedidos', methods=['GET'])
def listar_pedidos():
    pedidos = Pedido.query.all()
    return jsonify({
        "exito": True,
        "pedidos": [{
            "id": p.id,
            "cliente": p.cliente_nombre,
            "direccion": p.direccion,
            "total": p.total,
            "estado": p.estado,
            "sede_id": p.sede_id
        } for p in pedidos]
    })

@app.route('/api/pedidos/<orden_id>/estado', methods=['PUT'])
def actualizar_estado_pedido(orden_id):
    data = request.get_json() or {}
    nuevo_estado = data.get('estado')
    
    pedido = db.session.get(Pedido, orden_id) if hasattr(db.session, 'get') else Pedido.query.filter_by(id=orden_id).first()
    if not pedido:
        return jsonify({"exito": False, "mensaje": "Pedido no encontrado"}), 404
        
    pedido.estado = nuevo_estado
    db.session.commit()
    return jsonify({"exito": True, "mensaje": f"Estado actualizado a: {nuevo_estado}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

