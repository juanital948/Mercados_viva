const API = window.location.hostname.match(/localhost|127.0.0.1/) ? 'http://127.0.0.1:5001' : '';

const App = {
  sede: '', cat: [], cart: [], cacheInv: [],

  async init() {
    const res = await fetch(`${API}/api/sedes`).then(r => r.json()).catch(() => null);
    if (res?.exito && res.sedes.length) {
      document.getElementById('select-sede').innerHTML = res.sedes.map(s => `<option value="${s.id}">${s.nombre}</option>`).join('');
      this.sede = res.sedes[0].id;
      await this.cargarCatalogo();
    }
  },

  async cambiarSede() {
    this.sede = document.getElementById('select-sede').value;
    this.cart = [];
    this.renderCarrito();
    await this.cargarCatalogo();
  },

  async cargarCatalogo() {
    const res = await fetch(`${API}/api/sedes/${this.sede}/catalogo`).then(r => r.json());
    if (res.exito) { this.cat = res.productos; this.renderCatalogo(); }
  },

  renderCatalogo() {
    const grid = document.getElementById('grid-productos');
    if (!grid) return;
    if (!this.cat.length) { grid.innerHTML = '<p>No hay productos.</p>'; return; }
    
    grid.innerHTML = this.cat.map(p => {
      const out = p.stock <= 0;
      return `<div class="prod-card ${out ? 'out' : ''}">
        <div><strong>${p.nombre}</strong><p>$${p.precio.toLocaleString()}</p><small style="color:${out ? '#dc2626' : '#16a34a'};font-weight:600;">${out ? 'AGOTADO' : '● Disponible'}</small></div>
        <button class="btn-tab" ${out ? 'disabled' : ''} onclick="App.agregar('${p.id}')">${out ? 'Sin Stock' : '+ Agregar'}</button>
      </div>`;
    }).join('');
  },

  agregar(id) {
    const p = this.cat.find(x => x.id === id), item = this.cart.find(x => x.id === id);
    if (item) { if (item.cantidad < p.stock) item.cantidad++; else alert("Límite alcanzado."); }
    else this.cart.push({ id: p.id, nombre: p.nombre, precio: p.precio, cantidad: 1, stockMax: p.stock });
    this.renderCarrito();
  },

  renderCarrito() {
    const lista = document.getElementById('lista-carrito'), totalEl = document.getElementById('total-val');
    if (!lista || !totalEl) return;
    if (!this.cart.length) { lista.innerHTML = '<li class="empty">Carrito vacío.</li>'; totalEl.textContent = '0'; return; }
    let total = 0;
    lista.innerHTML = this.cart.map(i => { total += i.precio * i.cantidad; return `<li class="cart-item"><span>${i.nombre} x${i.cantidad}</span><strong>$${(i.precio*i.cantidad).toLocaleString()}</strong></li>`; }).join('');
    totalEl.textContent = total.toLocaleString();
  },

  async procesarCompra() {
    const cliente = { nombre: document.getElementById('cust-name').value.trim(), email: document.getElementById('cust-email').value.trim(), direccion: document.getElementById('cust-address').value.trim() };
    const metodo_pago = document.getElementById('pay-method').value, box = document.getElementById('status-box');
    box.className = "status-box info"; box.textContent = "Procesando...";

    const res = await fetch(`${API}/api/pedidos/crear`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ sede_id: this.sede, cliente, items: this.cart, metodo_pago }) }).then(r => r.json()).catch(() => null);
    
    if (res?.exito) {
      box.className = "status-box success"; box.innerHTML = `<strong>¡Orden creada!</strong> ID: ${res.orden_id}<br>${res.mensaje}`;
      this.cart = []; this.renderCarrito(); await this.cargarCatalogo();
    } else {
      box.className = "status-box error"; box.innerHTML = `<strong>Error:</strong> ${res?.mensaje || 'Falló la conexión'} ${res?.sugerencia ? '<br>'+res.sugerencia : ''}`;
    }
  },

  cambiarVista(vista) {
    document.getElementById('vista-cliente').classList.toggle('hidden', vista !== 'cliente');
    document.getElementById('vista-operador').classList.toggle('hidden', vista !== 'operador');
    document.getElementById('btn-vista-cliente').classList.toggle('active', vista === 'cliente');
    document.getElementById('btn-vista-operador').classList.toggle('active', vista === 'operador');
    document.getElementById('wrapper-sede').style.display = vista === 'cliente' ? 'block' : 'none';
    if (vista === 'operador') { this.cargarPedidosOperador(); this.cargarInventarioOperador(); }
  },

  async cargarPedidosOperador() {
    const res = await fetch(`${API}/api/pedidos`).then(r => r.json());
    const tbody = document.getElementById('tabla-pedidos');
    if (!tbody) return;
    tbody.innerHTML = res.exito && res.pedidos.length ? res.pedidos.map(p => `
      <tr><td><strong>${p.id}</strong></td><td>${p.cliente}</td><td>${p.direccion}</td><td>$${p.total.toLocaleString()}</td><td><span class="badge">${p.estado}</span></td>
      <td><select onchange="App.actualizarEstado('${p.id}', this.value)"><option value="">Cambiar...</option><option value="Empacado en Tienda">Empacado</option><option value="En Domicilio (En Camino)">En Camino</option><option value="Entregado al Cliente">Entregado</option></select></td></tr>
    `).join('') : `<tr><td colspan="6">No hay pedidos.</td></tr>`;
  },

  async cargarInventarioOperador() {
    const res = await fetch(`${API}/api/inventario-global`).then(r => r.json());
    if (res.exito) { this.cacheInv = res.inventario; this.renderInventarioOperador(); }
  },

  renderInventarioOperador() {
    let cont = document.getElementById('inventario-operador-container');
    if (!cont) {
      cont = document.createElement('div'); cont.id = 'inventario-operador-container'; cont.style.marginTop = '40px';
      document.getElementById('vista-operador').appendChild(cont);
    }
    const txt = document.getElementById('inv-search')?.value.toLowerCase() || '';
    const sedeFiltro = document.getElementById('inv-sede')?.value || 'todas';
    const sedesNames = this.cacheInv.map(i => i.sede);

    cont.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;border-top:2px solid #e5e7eb;padding-top:25px;flex-wrap:wrap;gap:15px;">
        <h2 style="margin:0;">Control de Inventario por Sede</h2>
        <div style="display:flex;gap:10px;flex:1;justify-content:flex-end;flex-wrap:wrap;">
          <select id="inv-sede" onchange="App.renderInventarioOperador()" style="padding:10px;border:1px solid #d1d5db;border-radius:6px;background:white;">
            <option value="todas">📍 Todas las Sedes</option>
            ${sedesNames.map(s => `<option value="${s}" ${sedeFiltro===s?'selected':''}>${s}</option>`).join('')}
          </select>
          <div style="position:relative;max-width:300px;flex:1;">
            <span style="position:absolute;left:12px;top:50%;transform:translateY(-50%);">🔍</span>
            <input type="text" id="inv-search" placeholder="Buscar producto..." value="${txt}" oninput="App.renderInventarioOperador()" style="width:100%;padding:10px 10px 10px 38px;border:1px solid #d1d5db;border-radius:6px;outline:none;" />
          </div>
        </div>
      </div>
      ${this.cacheInv.filter(i => sedeFiltro==='todas' || i.sede===sedeFiltro).map(i => {
        const prods = i.productos.filter(p => p.nombre.toLowerCase().includes(txt));
        if (!prods.length) return '';
        return `<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:15px;margin-bottom:25px;">
          <h3 style="margin-bottom:12px;color:#1f2937;">📍 Sede: ${i.sede}</h3>
          <table style="width:100%;border-collapse:collapse;background:white;border-radius:6px;overflow:hidden;">
            <thead><tr style="background:#f3f4f6;text-align:left;border-bottom:2px solid #e5e7eb;"><th style="padding:10px;">Producto</th><th style="padding:10px;">Precio</th><th style="padding:10px;">Stock</th><th style="padding:10px;">Estado</th></tr></thead>
            <tbody>${prods.map(p => {
              const out = p.stock <= 0;
              return `<tr style="border-bottom:1px solid #f3f4f6;"><td style="padding:10px;"><strong>${p.nombre}</strong></td><td style="padding:10px;">$${p.precio.toLocaleString()}</td><td style="padding:10px;"><strong>${p.stock} u.</strong></td><td style="padding:10px;"><span style="padding:4px 8px;border-radius:4px;font-weight:600;font-size:12px;background:${out?'#fee2e2':'#dcfce7'};color:${out?'#991b1b':'#166534'};">${out?'AGOTADO':'DISPONIBLE'}</span></td></tr>`;
            }).join('')}</tbody>
          </table>
        </div>`;
      }).join('') || '<p style="text-align:center;color:#6b7280;padding:20px;">No se encontraron resultados.</p>'}
    `;
    const input = document.getElementById('inv-search');
    if (input) { input.focus(); input.setSelectionRange(input.value.length, input.value.length); }
  },

  async actualizarEstado(id, estado) {
    if (!estado) return;
    const res = await fetch(`${API}/api/pedidos/${id}/estado`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ estado }) }).then(r => r.json());
    if (res.exito) await this.cargarPedidosOperador();
    else alert(res.mensaje);
  }
};

document.addEventListener('DOMContentLoaded', () => App.init());// update app.js
