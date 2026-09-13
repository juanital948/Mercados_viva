import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Sede(db.Model):
    __tablename__ = 'sedes'
    id = db.Column(db.String(50), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    productos = db.relationship('Producto', backref='sede', lazy=True)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.String(50), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    sede_id = db.Column(db.String(50), db.ForeignKey('sedes.id'), nullable=False)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.String(50), primary_key=True)
    cliente_nombre = db.Column(db.String(100), nullable=False)
    cliente_email = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    sede_id = db.Column(db.String(50), db.ForeignKey('sedes.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(50), default="Registrado")  # Registrado -> Empacado -> En Camino -> Entregado
    metodo_pago = db.Column(db.String(50), nullable=False)
    pagado = db.Column(db.Boolean, default=False)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Sembrar datos iniciales si está vacía
        if not Sede.query.first():
            s1 = Sede(id="sede_norte", nombre="Sede Norte (Poblado)")
            s2 = Sede(id="sede_centro", nombre="Sede Centro (La Candelaria)")
            s3 = Sede(id="sede_sur", nombre="Sede Sur (Envigado)")
            
            db.session.add_all([s1, s2, s3])
            db.session.commit()

            prods = [
                Producto(id="p1_norte", nombre="Arroz 1kg", precio=5000, stock=10, sede_id="sede_norte"),
                Producto(id="p2_norte", nombre="Leche 1L", precio=4000, stock=0, sede_id="sede_norte"),
                Producto(id="p3_norte", nombre="Huevos x12", precio=9000, stock=5, sede_id="sede_norte"),
                
                Producto(id="p1_centro", nombre="Arroz 1kg", precio=5000, stock=20, sede_id="sede_centro"),
                Producto(id="p2_centro", nombre="Leche 1L", precio=4000, stock=8, sede_id="sede_centro"),
                Producto(id="p3_centro", nombre="Huevos x12", precio=9000, stock=0, sede_id="sede_centro"),
                
                Producto(id="p1_sur", nombre="Arroz 1kg", precio=5000, stock=0, sede_id="sede_sur"),
                Producto(id="p2_sur", nombre="Leche 1L", precio=4000, stock=15, sede_id="sede_sur"),
                Producto(id="p3_sur", nombre="Huevos x12", precio=9000, stock=10, sede_id="sede_sur")
            ]
            db.session.add_all(prods)
            db.session.commit()