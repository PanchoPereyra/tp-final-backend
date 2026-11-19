from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

USUARIOS_DB = {
    1: {
        "id": 1,
        "name": "María Gómez",
        "email": "maria@ejemplo.com",
        "edad": 28,
        "pais": "Argentina",
        "roles": ["admin", "editor"],
    },
    2: {
        "id": 2,
        "name": "Tomás Pérez",
        "email": "tomas@ejemplo.com",
        "edad": 34,
        "pais": "Uruguay",
        "roles": ["user"],
    },
    3: {
        "id": 3,
        "name": "Lucía #1",
        "email": "lucia@ejemplo.com",
        "edad": 25,
        "pais": "Chile",
        "roles": ["user"],
    },
}


@app.get("/user")
def listar_usuarios():
    return [{"id": u["id"], "name": u["name"]} for u in USUARIOS_DB.values()]


# IMPORTANTE: declarar /user/search/{name} antes de /user/{user_id}
@app.get("/user/search/{name}")
def buscar_usuarios(name: str):
    termino = name.strip().lower()
    coincidencias = [
        {"id": u["id"], "name": u["name"]}
        for u in USUARIOS_DB.values()
        if termino in u["name"].lower()
    ]
    return coincidencias


@app.get("/user/{user_id}")
def obtener_usuario(user_id: int):
    usuario = USUARIOS_DB.get(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.get("/", response_class=HTMLResponse)
def vista_busqueda():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <title>Práctica 3 - Buscar por nombre</title>
      <style>
        body { font-family: sans-serif; display: flex; gap: 3rem; padding: 2rem; }
        .controles { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
        li { cursor: pointer; margin-bottom: 0.4rem; }
        li:hover { text-decoration: underline; }
      </style>
    </head>
    <body>
      <div>
        <h2>Usuarios</h2>

        <div class="controles">
          <input id="inputNombre" type="text" placeholder="Ej: ma o #" />
          <button id="btnBuscar" type="button">Buscar</button>
          <button id="btnLimpiar" type="button">Limpiar</button>
        </div>

        <p id="estado"></p>
        <ul id="lista"></ul>
      </div>

      <div>
        <h2>Detalle</h2>
        <div id="detalle"><p>Hacé clic en un nombre para ver sus datos.</p></div>
      </div>

      <script>
        const inputNombre = document.getElementById("inputNombre");
        const btnBuscar = document.getElementById("btnBuscar");
        const btnLimpiar = document.getElementById("btnLimpiar");
        const estadoEl = document.getElementById("estado");
        const listaEl = document.getElementById("lista");
        const detalleEl = document.getElementById("detalle");

        function renderLista(usuarios) {
          listaEl.innerHTML = "";
          if (usuarios.length === 0) {
            estadoEl.textContent = "No se encontraron usuarios.";
            return;
          }
          estadoEl.textContent = "";
          usuarios.forEach((user) => {
            const li = document.createElement("li");
            li.textContent = user.name;
            li.onclick = () => cargarDetalle(user.id);
            listaEl.appendChild(li);
          });
        }

        async function cargarTodos() {
          estadoEl.textContent = "Cargando...";
          listaEl.innerHTML = "";
          try {
            const res = await fetch("/user");
            const data = await res.json();
            if (!res.ok) {
              estadoEl.textContent = data.detail || "Error al cargar usuarios";
              return;
            }
            renderLista(data);
          } catch (err) {
            estadoEl.textContent = "Error de conexión";
          }
        }

        async function buscarPorNombre() {
          const valor = inputNombre.value;
          if (!valor.trim()) {
            cargarTodos();
            return;
          }

          estadoEl.textContent = "Cargando...";
          listaEl.innerHTML = "";

          // Con encodeURIComponent se escapa "#" como "%23" para que no sea fragmento de URL
          const url = `/user/search/${encodeURIComponent(valor)}`;
          try {
            const res = await fetch(url);
            const data = await res.json();
            if (!res.ok) {
              estadoEl.textContent = data.detail || "Error en la búsqueda";
              return;
            }
            renderLista(data);
          } catch (err) {
            estadoEl.textContent = "Error al buscar";
          }
        }

        async function cargarDetalle(id) {
          detalleEl.innerHTML = "<p>Cargando...</p>";
          try {
            const res = await fetch(`/user/${id}`);
            const data = await res.json();
            if (!res.ok) {
              detalleEl.innerHTML = `<p>${data.detail || "Error al cargar detalle"}</p>`;
              return;
            }
            detalleEl.innerHTML = `
              <p><strong>Email:</strong> ${data.email}</p>
              <p><strong>Edad:</strong> ${data.edad}</p>
              <p><strong>País:</strong> ${data.pais}</p>
              <p><strong>Roles:</strong> ${data.roles.join(", ")}</p>
            `;
          } catch (err) {
            detalleEl.innerHTML = "<p>Error de conexión</p>";
          }
        }

        btnBuscar.addEventListener("click", buscarPorNombre);
        inputNombre.addEventListener("keydown", (e) => {
          if (e.key === "Enter") buscarPorNombre();
        });
        btnLimpiar.addEventListener("click", () => {
          inputNombre.value = "";
          cargarTodos();
        });

        cargarTodos();
      </script>
    </body>
    </html>
    """