import pytest
from app import app, db
from backend.database import Sede, Producto

@pytest.fixture
def client():
    app.config['TESTING'] = True 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            # Limpiamos y creamos las tablas desde cero para cada prueba
            db.drop_all()
            db.create_all()
            
            sede_norte = Sede(id="sede_norte", nombre="Sede Norte")
            db.session.add(sede_norte)
            
            producto = Producto(
                id="p1_norte",
                nombre="Arroz 1kg",
                precio=5000,
                stock=10,
                sede_id="sede_norte"
            )
            db.session.add(producto)
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_obtener_sedes_y_catalogo(client):
    res_sedes = client.get('/api/sedes')
    assert res_sedes.status_code == 200
    sedes = res_sedes.get_json()['sedes']
    assert len(sedes) > 0

    res_cat = client.get(f"/api/sedes/{sedes[0]['id']}/catalogo")
    assert res_cat.status_code == 200
    assert 'productos' in res_cat.get_json()

def test_crear_pedido_exitoso(client):
    payload = {
        "sede_id": "sede_norte",
        "cliente": {"nombre": "Juan Pérez", "email": "juan@example.com", "direccion": "Calle 50 #10-20"},
        "items": [{"id": "p1_norte", "nombre": "Arroz 1kg", "precio": 5000, "cantidad": 2}],
        "metodo_pago": "Tarjeta de Crédito"
    }
    res = client.post('/api/pedidos/crear', json=payload)
    assert res.status_code == 201
    assert res.get_json()['exito'] is True

def test_compra_caso_excepcional_stock_insuficiente(client):
    payload = {
        "sede_id": "sede_norte",
        "cliente": {"nombre": "Ana López", "email": "ana@example.com", "direccion": "Cra 43 #12-05"},
        "items": [{"id": "p1_norte", "nombre": "Arroz 1kg", "precio": 5000, "cantidad": 999}],
        "metodo_pago": "PSE"
    }
    res = client.post('/api/pedidos/crear', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data['exito'] is False
    assert "Stock insuficiente" in data['mensaje']