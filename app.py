from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Tu clave de NewsAPI
NEWS_API_KEY = "8cbe1015110a403e9a8439f338d0f6aa"

# Todo el frontend empaquetado en una variable
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LINC - Inteligencia Global</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
    <style>
        :root {
            --bg-body: #0a0a0a;
            --bg-header: #111111;
            --bg-card: #111111;
            --bg-inner: #0d0d0d;
            --text-main: #e0e0e0;
            --text-muted: #888888;
            --border-color: #222222;
            --border-input: #333333;
            --accent: #cc0000;
            --accent-hover: #aa0000;
        }

        [data-theme="light"] {
            --bg-body: #eef2f5;
            --bg-header: #ffffff;
            --bg-card: #ffffff;
            --bg-inner: #f8fafc;
            --text-main: #1f2937;
            --text-muted: #6b7280;
            --border-color: #d1d5db;
            --border-input: #d1d5db;
            --accent: #cc0000;
            --accent-hover: #aa0000;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: var(--bg-body); 
            color: var(--text-main); 
            height: 100vh; 
            display: flex;
            flex-direction: column;
            overflow: hidden; 
            transition: background 0.3s, color 0.3s;
        }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-card); border-radius: 4px; }
        ::-webkit-scrollbar-thumb { background: var(--border-input); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

        header { 
            background: var(--bg-header); 
            padding: 15px 30px; 
            border-bottom: 2px solid var(--accent); 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            flex-shrink: 0;
            transition: background 0.3s;
        }
        header h1 { font-size: 24px; color: var(--text-main); letter-spacing: 6px; font-weight: 800; }
        header span { color: var(--accent); }
        header p { color: var(--text-muted); font-size: 11px; letter-spacing: 1px; text-transform: uppercase; }

        .header-controls { display: flex; gap: 12px; align-items: center; }
        .btn-icon { background: var(--bg-inner); color: var(--text-main); border: 1px solid var(--border-color); padding: 8px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 700; transition: all 0.2s; }
        .btn-icon:hover { border-color: var(--accent); color: var(--accent); }
        .user-status { font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; }

        .main-layout { 
            flex: 1; 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 20px; 
            padding: 20px; 
            min-height: 0; 
        }

        .card { 
            background: var(--bg-card); 
            border-radius: 4px; 
            padding: 20px; 
            border: 1px solid var(--border-color); 
            display: flex;
            flex-direction: column;
            min-height: 0; 
            transition: background 0.3s, border-color 0.3s;
        }
        
        .card h2 { 
            font-size: 12px; color: var(--accent); margin-bottom: 15px; 
            text-transform: uppercase; letter-spacing: 3px; 
            font-weight: 700; border-left: 3px solid var(--accent); padding-left: 10px; 
            flex-shrink: 0;
        }

        .card-mapa { height: 100%; }
        #mapa { flex: 1; width: 100%; border-radius: 4px; border: 1px solid var(--border-color); z-index: 1; }

        .panel-derecho { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: auto auto 1fr; gap: 16px; height: 100%; min-height: 0; }

        .categorias-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .categoria-btn { background: var(--bg-inner); border: 2px solid var(--border-input); color: var(--text-main); padding: 10px; border-radius: 4px; cursor: pointer; text-align: center; font-size: 11px; font-weight: 700; text-transform: uppercase; transition: all 0.2s; }
        .categoria-btn:hover { border-color: var(--accent); }
        .categoria-btn.activo { background: var(--accent); border-color: var(--accent); color: #fff; }

        #dashboard-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .stat { background: var(--bg-inner); border-radius: 4px; padding: 10px; text-align: center; border: 1px solid var(--border-color); }
        .stat .numero { font-size: 24px; color: var(--accent); font-weight: 800; line-height: 1; }
        .stat .label { font-size: 9px; color: var(--text-muted); text-transform: uppercase; margin-top: 6px; }

        .search-box { display: flex; gap: 8px; margin-bottom: 12px; flex-shrink: 0; }
        .search-box input { flex: 1; background: var(--bg-inner); border: 1px solid var(--border-input); border-radius: 4px; padding: 10px; color: var(--text-main); font-size: 12px; outline: none; transition: background 0.3s; }
        .search-box input:focus { border-color: var(--accent); }
        .search-box button { background: var(--accent); color: #fff; border: none; padding: 10px 16px; border-radius: 4px; font-weight: 700; cursor: pointer; text-transform: uppercase; font-size: 11px; }
        .search-box button:hover { background: var(--accent-hover); }

        #resultados-busqueda, #noticias-lista { flex: 1; overflow-y: auto; padding-right: 5px; }

        .evento-item { background: var(--bg-inner); border-radius: 4px; padding: 10px; margin-bottom: 8px; border-left: 3px solid var(--accent); font-size: 11px; transition: background 0.3s; }
        .evento-item .titulo { color: var(--accent); font-weight: 700; margin-bottom: 4px; }
        .evento-item .desc { color: var(--text-muted); line-height: 1.4; margin-bottom: 4px; }
        .evento-item .meta { color: var(--text-muted); font-size: 9px; opacity: 0.8; }
        .sin-datos { color: var(--text-muted); text-align: center; padding: 20px; font-size: 12px; }

        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 1000; justify-content: center; align-items: center; backdrop-filter: blur(4px); }
        .modal-overlay.activo { display: flex; }
        .modal-caja { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; width: 350px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .modal-caja h3 { color: var(--accent); margin-bottom: 20px; text-transform: uppercase; font-size: 14px; letter-spacing: 2px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;}
        
        .ajuste-item { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .ajuste-item span { font-size: 12px; font-weight: 700; color: var(--text-main); text-transform: uppercase; }
        
        .input-login { width: 100%; background: var(--bg-inner); border: 1px solid var(--border-input); padding: 10px; color: var(--text-main); margin-bottom: 10px; border-radius: 4px; outline: none; font-size: 12px;}
        .input-login:focus { border-color: var(--accent); }
        .btn-full { width: 100%; background: var(--accent); color: #fff; border: none; padding: 12px; font-weight: 700; border-radius: 4px; cursor: pointer; text-transform: uppercase; font-size: 11px; margin-top: 10px;}
        .btn-full:hover { background: var(--accent-hover); }

        .btn-cerrar-modal { background: transparent; border: 1px solid var(--border-color); color: var(--text-main); width: 100%; padding: 10px; margin-top: 10px; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: 700; text-transform: uppercase; }
        .btn-cerrar-modal:hover { background: var(--bg-inner); }

        @media (max-width: 1024px) {
            body { height: auto; overflow: visible; }
            .main-layout { grid-template-columns: 1fr; min-height: 100vh; }
            .panel-derecho { grid-template-columns: 1fr; grid-template-rows: auto; }
            #mapa { height: 400px; flex: none; }
            #resultados-busqueda, #noticias-lista { max-height: 300px; }
        }
    </style>
</head>
<body>
    <header>
        <div>
            <h1>LI<span>N</span>C</h1>
            <p>Plataforma Global de Inteligencia</p>
        </div>
        <div class="header-controls">
            <span id="estado-usuario" class="user-status">Desconectado</span>
            <button class="btn-icon" onclick="abrirModal()">⚙️ Ajustes</button>
        </div>
    </header>

    <div class="main-layout">
        <!-- MAPA INTERACTIVO -->
        <div class="card card-mapa">
            <h2>Mapa de Eventos Globales</h2>
            <div id="mapa"></div>
        </div>

        <!-- PANEL DERECHO -->
        <div class="panel-derecho">
            <div class="card">
                <h2>Impacto</h2>
                <div id="dashboard-stats"></div>
            </div>

            <div class="card">
                <h2>Inteligencia Interna</h2>
                <div class="search-box">
                    <input type="text" id="input-busqueda" placeholder="Palabra clave interna..." onkeydown="if(event.key==='Enter') buscarTexto()">
                    <button onclick="buscarTexto()">Buscar</button>
                </div>
                <div id="resultados-busqueda"></div>
            </div>

            <!-- FEED DE NOTICIAS OSINT -->
            <div class="card" style="grid-column: 1 / -1;">
                <h2>📰 Feed de Noticias OSINT</h2>
                
                <div class="search-box">
                    <input type="text" id="input-noticias" placeholder="Buscar en noticias externas (ej: ciberseguridad)..." onkeydown="if(event.key==='Enter') buscarNoticiasManual()">
                    <button onclick="buscarNoticiasManual()">Rastrear</button>
                </div>

                <div class="categorias-grid" style="margin-bottom: 12px; grid-template-columns: repeat(4, 1fr);">
                    <button class="categoria-btn activo" onclick="filtrarNoticias('politica', this)">🏛️ Política</button>
                    <button class="categoria-btn" onclick="filtrarNoticias('economia', this)">💼 Economía</button>
                    <button class="categoria-btn" onclick="filtrarNoticias('tecnologia', this)">💻 Tecnología</button>
                    <button class="categoria-btn" onclick="filtrarNoticias('seguridad', this)">🛡️ Seguridad</button>
                </div>

                <div id="noticias-lista" style="flex: 1; overflow-y: auto; padding-right: 5px; min-height: 250px;">
                    <!-- Las noticias se inyectarán aquí -->
                </div>
            </div>
        </div>
    </div>

    <!-- MODAL -->
    <div id="modal-ajustes" class="modal-overlay">
        <div class="modal-caja">
            <h3>⚙️ Panel de Control</h3>
            <div class="ajuste-item">
                <span>Tema Visual</span>
                <button class="btn-icon" id="btn-toggle-tema" onclick="alternarTema()">🌙 Cambiar a Claro</button>
            </div>
            <div id="seccion-login">
                <h3 style="margin-top: 30px;">Acceso Operativo</h3>
                <input type="text" id="user-input" class="input-login" placeholder="Usuario de Agente">
                <input type="password" id="pass-input" class="input-login" placeholder="Clave de Acceso">
                <button class="btn-full" onclick="iniciarSesion()">Iniciar Sesión</button>
            </div>
            <div id="seccion-logout" style="display: none;">
                <h3 style="margin-top: 30px;">Sesión Activa</h3>
                <button class="btn-full" style="background: var(--bg-inner); border: 1px solid var(--border-color); color: var(--text-main);" onclick="cerrarSesion()">Cerrar Sesión</button>
            </div>
            <button class="btn-cerrar-modal" onclick="cerrarModal()">Cerrar Panel</button>
        </div>
    </div>

    <script>
        let isDarkMode = true;
        let isLogged = false;
        let mapa, capaMarcadores, capaBase;
        
        function inicializarMapa() {
            mapa = L.map('mapa').setView([20, 0], 2);
            capaMarcadores = L.layerGroup().addTo(mapa);
            actualizarCapaMapa();
            window.addEventListener('resize', () => { if (mapa) setTimeout(() => mapa.invalidateSize(), 200); });
        }

        function actualizarCapaMapa() {
            if (capaBase) { mapa.removeLayer(capaBase); }
            const tileUrl = isDarkMode 
                ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
                : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
            capaBase = L.tileLayer(tileUrl, { attribution: '© OSM', maxZoom: 19 }).addTo(mapa);
        }

        function alternarTema() {
            const htmlTag = document.documentElement;
            const btnTema = document.getElementById('btn-toggle-tema');
            if (isDarkMode) {
                htmlTag.setAttribute('data-theme', 'light');
                btnTema.innerHTML = "🌑 Cambiar a Oscuro";
                isDarkMode = false;
            } else {
                htmlTag.setAttribute('data-theme', 'dark');
                btnTema.innerHTML = "🌙 Cambiar a Claro";
                isDarkMode = true;
            }
            actualizarCapaMapa(); 
        }

        function abrirModal() { document.getElementById('modal-ajustes').classList.add('activo'); }
        function cerrarModal() { document.getElementById('modal-ajustes').classList.remove('activo'); }

        function iniciarSesion() {
            const user = document.getElementById('user-input').value.trim();
            if(!user) return;
            isLogged = true;
            document.getElementById('estado-usuario').innerText = `Agente: ${user}`;
            document.getElementById('estado-usuario').style.color = 'var(--accent)';
            document.getElementById('seccion-login').style.display = 'none';
            document.getElementById('seccion-logout').style.display = 'block';
            cerrarModal();
        }

        function cerrarSesion() {
            isLogged = false;
            document.getElementById('estado-usuario').innerText = "Desconectado";
            document.getElementById('estado-usuario').style.color = 'var(--text-muted)';
            document.getElementById('user-input').value = "";
            document.getElementById('pass-input').value = "";
            document.getElementById('seccion-login').style.display = 'block';
            document.getElementById('seccion-logout').style.display = 'none';
            cerrarModal();
        }

        function cargarDashboard() {
            document.getElementById('dashboard-stats').innerHTML = `
                <div class="stat"><div class="numero">142</div><div class="label">Docs</div></div>
                <div class="stat"><div class="numero">89</div><div class="label">Nodos</div></div>
                <div class="stat"><div class="numero">45</div><div class="label">Pol</div></div>
                <div class="stat"><div class="numero">32</div><div class="label">Eco</div></div>
            `;
        }

        function buscarTexto() {
            const q = document.getElementById('input-busqueda').value.trim();
            if (!q) return;
            document.getElementById('resultados-busqueda').innerHTML = `
                <div class="evento-item">
                    <div class="titulo">📄 Búsqueda Interna: ${q}</div>
                    <div class="desc">Buscando en la base de datos clasificada...</div>
                </div>`;
        }

        let temaNoticiasActual = "politica";
        let intervaloRefresh;

        async function cargarNoticias(tema = temaNoticiasActual) {
            const contenedor = document.getElementById('noticias-lista');
            contenedor.innerHTML = '<div class="sin-datos">Cargando inteligencia de fuentes abiertas (APIs Reales)... ⏳</div>';

            try {
                // Llama al backend local de Python
                const res = await fetch(`/noticias?tema=${encodeURIComponent(tema)}`);
                if (!res.ok) throw new Error("Error en la conexión con el servidor LINC.");
                
                const data = await res.json();
                
                if (!data.noticias || data.noticias.length === 0) {
                    contenedor.innerHTML = '<div class="sin-datos">No hay noticias relevantes en este momento.</div>';
                    return;
                }

                contenedor.innerHTML = data.noticias.map(n => `
                    <div class="evento-item">
                        <div style="display: flex; gap: 10px; margin-bottom: 6px;">
                            ${n.imagen ? `<img src="${n.imagen}" alt="img" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid var(--border-color);">` : ''}
                            <div>
                                <div class="titulo">${n.titulo}</div>
                                <div class="meta">📰 ${n.fuente} | 🕒 ${n.fecha}</div>
                            </div>
                        </div>
                        <div class="desc">${n.descripcion}</div>
                        <a href="${n.url}" target="_blank" style="color: var(--accent); font-size: 10px; text-decoration: none; font-weight: bold; margin-top: 5px; display: inline-block;">[LEER MÁS ↗]</a>
                    </div>
                `).join('');
                
            } catch (error) {
                console.error("Error cargando noticias:", error);
                contenedor.innerHTML = '<div class="sin-datos" style="color: var(--accent);">Error al conectar con la API de noticias.</div>';
            }
        }

        function buscarNoticiasManual() {
            const query = document.getElementById('input-noticias').value.trim();
            if (query) {
                temaNoticiasActual = query;
                document.querySelectorAll('#noticias-lista').parentElement.querySelectorAll('.categoria-btn').forEach(b => b.classList.remove('activo'));
                cargarNoticias(query);
                reiniciarAutoRefresh();
            }
        }

        function filtrarNoticias(tema, btnElement) {
            btnElement.parentElement.querySelectorAll('.categoria-btn').forEach(b => b.classList.remove('activo'));
            btnElement.classList.add('activo');
            document.getElementById('input-noticias').value = '';
            temaNoticiasActual = tema;
            cargarNoticias(tema);
            reiniciarAutoRefresh();
        }

        function iniciarAutoRefresh(segundos = 60) {
            intervaloRefresh = setInterval(() => {
                cargarNoticias(temaNoticiasActual);
            }, segundos * 1000);
        }

        function reiniciarAutoRefresh() {
            clearInterval(intervaloRefresh);
            iniciarAutoRefresh(60);
        }

        window.onload = () => {
            inicializarMapa();
            cargarDashboard();
            cargarNoticias();
            iniciarAutoRefresh(60);
            setTimeout(() => mapa.invalidateSize(), 500);
        };
    </script>
</body>
</html>
"""

# ---------------------------------------------------------
# RUTAS DE FLASK
# ---------------------------------------------------------

@app.route('/')
def index():
    # Retorna directamente el HTML al entrar a http://localhost:5000/
    return DASHBOARD_HTML

@app.route('/noticias', methods=['GET'])
def obtener_noticias():
    tema = request.args.get('tema', 'politica')
    url = f"https://newsapi.org/v2/everything?q={tema}&language=es&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    
    try:
        respuesta = requests.get(url)
        datos = respuesta.json()
        noticias_formateadas = []
        
        if datos.get('status') == 'ok':
            articulos = datos.get('articles', [])[:10]
            
            for articulo in articulos:
                if articulo.get('title') == '[Removed]':
                    continue
                    
                fecha_raw = articulo.get('publishedAt', '')
                fecha_limpia = fecha_raw.replace('T', ' ')[:16] if fecha_raw else 'Reciente'

                noticias_formateadas.append({
                    "titulo": articulo.get('title', 'Sin título'),
                    "url": articulo.get('url', '#'),
                    "fuente": articulo.get('source', {}).get('name', 'Fuente global'),
                    "fecha": fecha_limpia,
                    "categoria": tema,
                    "descripcion": articulo.get('description') or "Sin descripción disponible.",
                    "imagen": articulo.get('urlToImage')
                })
        
        return jsonify({
            "tema": tema,
            "cantidad": len(noticias_formateadas),
            "noticias": noticias_formateadas
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "No se pudo conectar a la fuente de inteligencia."}), 500

if __name__ == '__main__':
    print("Iniciando nodo LINC. Abre http://localhost:5000 en tu navegador.")
app.run(host='0.0.0.0', port=5000) 