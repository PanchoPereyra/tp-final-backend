from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

TOKEN_VALIDO = "token-valido-123"

USUARIOS_DB = [
    {"id": 1, "name": "Martina", "age": 27},
    {"id": 2, "name": "Lucas", "age": 31},
    {"id": 3, "name": "sfer", "age": 16},
]


class LoginRequest(BaseModel):
    email: str
    password: str


def verificar_token(authorization: str | None = Header(default=None)) -> str:
    # Centralizado en un solo lugar en el backend: si cambia el header, se edita acá
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token faltante",
        )
    token = authorization.removeprefix("Bearer ").strip()
    if token != TOKEN_VALIDO:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o vencido",
        )
    return token


@app.post("/login")
def login(payload: LoginRequest):
    if not payload.email.strip() or not payload.password.strip():
        raise HTTPException(status_code=400, detail="Credenciales incompletas")
    return {"access_token": TOKEN_VALIDO}


@app.get("/user")
def listar_usuarios(_token: str = Depends(verificar_token)):
    return USUARIOS_DB


@app.get("/", response_class=HTMLResponse)
def vista_practica_9():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <title>Práctica 9 - Refactorización y control de repetición</title>
      <style>
        body { font-family: sans-serif; padding: 2rem; max-width: 720px; }
        .hidden { display: none; }
        .caja { border: 1px solid #ccc; padding: 1rem; margin-bottom: 1rem; border-radius: 6px; }
        .error { color: #b00020; font-weight: bold; }
        button { cursor: pointer; margin-right: 0.5rem; }
      </style>
    </head>
    <body>
      <h1>Práctica 9: Cliente centralizado (sin repetir headers ni 401)</h1>

      <div class="caja">
        <strong>Auditoría en esta vista:</strong>
        <p>Header de token definido en un único lugar dentro de <code>apiFetch</code>.</p>
        <p>Llamadas realizadas a través de <code>apiFetch</code>: <span id="contadorFetch">0</span></p>
      </div>

      <p id="mensaje" class="error"></p>

      <div id="loginView" class="caja">
        <h2>Iniciar sesión</h2>
        <form id="loginForm">
          <input id="email" type="email" placeholder="Email" required />
          <input id="password" type="password" placeholder="Contraseña" required />
          <button type="submit">Entrar</button>
        </form>
      </div>

      <div id="appView" class="caja hidden">
        <h2>Usuarios</h2>
        <button id="btnRecargar" type="button">Recargar usuarios</button>
        <button id="btnLogout" type="button">Cerrar sesión</button>
        <p id="estadoCarga"></p>
        <ul id="lista"></ul>
      </div>

      <script>
        const API_BASE = "";
        const loginView = document.getElementById("loginView");
        const appView = document.getElementById("appView");
        const loginForm = document.getElementById("loginForm");
        const btnRecargar = document.getElementById("btnRecargar");
        const btnLogout = document.getElementById("btnLogout");
        const listaEl = document.getElementById("lista");
        const mensajeEl = document.getElementById("mensaje");
        const estadoCargaEl = document.getElementById("estadoCarga");
        const contadorFetchEl = document.getElementById("contadorFetch");

        let llamadasApiFetch = 0;

        function cerrarSesion(motivo = "") {
          localStorage.removeItem("token");
          mensajeEl.textContent = motivo;
          appView.classList.add("hidden");
          loginView.classList.remove("hidden");
        }

        function mostrarApp() {
          mensajeEl.textContent = "";
          loginView.classList.add("hidden");
          appView.classList.remove("hidden");
        }

        // Único punto donde se arma el header de autenticación y se intercepta el 401
        async function apiFetch(path, options = {}, onUnauthorized = null) {
          llamadasApiFetch += 1;
          contadorFetchEl.textContent = String(llamadasApiFetch);

          const token = localStorage.getItem("token");
          const headers = {
            ...(options.headers || {}),
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          };

          const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

          if (res.status === 401) {
            if (typeof onUnauthorized === "function") {
              onUnauthorized("Tu sesión venció");
            }
            return null;
          }

          return res;
        }

        async function cargarUsuarios() {
          estadoCargaEl.textContent = "Cargando...";
          listaEl.innerHTML = "";

          try {
            const res = await apiFetch("/user", {}, (msg) => cerrarSesion(msg));
            if (!res) return;

            const data = await res.json();
            if (!res.ok) {
              estadoCargaEl.textContent = "";
              mensajeEl.textContent = data.detail || `Error ${res.status}`;
              return;
            }

            estadoCargaEl.textContent = "";
            data.forEach((u) => {
              const li = document.createElement("li");
              li.textContent = `${u.name} (edad: ${u.age})`;
              listaEl.appendChild(li);
            });
            mostrarApp();
          } catch (err) {
            estadoCargaEl.textContent = "";
            mensajeEl.textContent = "Error de red al consultar la API";
          }
        }

        loginForm.addEventListener("submit", async (e) => {
          e.preventDefault();
          mensajeEl.textContent = "";

          const res = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: document.getElementById("email").value,
              password: document.getElementById("password").value,
            }),
          });

          const data = await res.json();
          if (!res.ok) {
            mensajeEl.textContent = data.detail || "Error al iniciar sesión";
            return;
          }

          localStorage.setItem("token", data.access_token);
          await cargarUsuarios();
        });

        btnRecargar.addEventListener("click", cargarUsuarios);
        btnLogout.addEventListener("click", () => cerrarSesion(""));

        if (localStorage.getItem("token")) {
          cargarUsuarios();
        }
      </script>
    </body>
    </html>
    """