from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

USUARIOS_DB = {
    1: {
        "id": 1,
        "name": "Ana Gómez",
        "email": "ana@ejemplo.com",
        "edad": 28,
        "pais": "Argentina",
        "roles": ["admin", "editor"],
    },
    2: {
        "id": 2,
        "name": "Lucas Pérez",
        "email": "lucas@ejemplo.com",
        "edad": 34,
        "pais": "Uruguay",
        "roles": ["user"],
    },
}


@app.get("/user")
def listar_usuarios():
    # Devuelve solo id y name en la lista
    return [{"id": u["id"], "name": u["name"]} for u in USUARIOS_DB.values()]


@app.get("/user/{user_id}")
def obtener_usuario(user_id: int):
    usuario = USUARIOS_DB.get(user_id)
    if not usuario:
        # FastAPI responde con HTTP 404 y {"detail": "..."}
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.get("/", response_class=HTMLResponse)
def vista_usuarios():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <title>Usuarios - FastAPI</title>
      <style>
        body { font-family: sans-serif; display: flex; gap: 3rem; padding: 2rem; }
        li { cursor: pointer; margin-bottom: 0.4rem; }
        li:hover { text-decoration: underline; }
      </style>
    </head>
    <body>
      <div>
        <h2>Usuarios</h2>
        <p id="estado">Cargando...</p>
        <ul id="lista"></ul>
      </div>

      <div>
        <h2>Detalle</h2>
        <div id="detalle"><p>Hacé clic en un nombre.</p></div>
      </div>

      <script>
        const estadoEl = document.getElementById("estado");
        const listaEl = document.getElementById("lista");
        const detalleEl = document.getElementById("detalle");

        async function cargarLista() {
          estadoEl.textContent = "Cargando...";
          listaEl.innerHTML = "";

          try {
            // Cambiá "/user" por "/usr" para probar el error 404 y ver "detail"
            const res = await fetch("/user");
            const data = await res.json();

            if (!res.ok) {
              estadoEl.textContent = data.detail || "Error en la API";
              return;
            }

            estadoEl.textContent = "";
            data.forEach((user) => {
              const li = document.createElement("li");
              li.textContent = user.name;
              li.onclick = () => cargarDetalle(user.id);
              listaEl.appendChild(li);
            });
          } catch (err) {
            estadoEl.textContent = "Error de conexión con el servidor";
          }
        }

        async function cargarDetalle(id) {
          detalleEl.innerHTML = "<p>Cargando...</p>";
          try {
            const res = await fetch(`/user/${id}`);
            const data = await res.json();

            if (!res.ok) {
              detalleEl.innerHTML = `<p>${data.detail || "Error al obtener detalle"}</p>`;
              return;
            }

            detalleEl.innerHTML = `
              <p><strong>Email:</strong> ${data.email}</p>
              <p><strong>Edad:</strong> ${data.edad}</p>
              <p><strong>País:</strong> ${data.pais}</p>
              <p><strong>Roles:</strong> ${data.roles.join(", ")}</p>
            `;
          } catch (err) {
            detalleEl.innerHTML = "<p>Error al cargar el detalle</p>";
          }
        }

        cargarLista();
      </script>
    </body>
    </html>
    """