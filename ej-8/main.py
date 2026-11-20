from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

TOKEN_VALIDO = "token-valido-123"

USUARIOS_DB = [
    {"id": 1, "name": "Martina"},
    {"id": 2, "name": "Lucas"},
    {"id": 3, "name": "sfer"},
]


class LoginRequest(BaseModel):
    email: str
    password: str


def verificar_token(authorization: str | None = Header(default=None)) -> str:
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
def vista_sesion_vencida():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <title>Práctica 8 - Sesión vencida</title>
      <style>
        body { font-family: sans-serif; padding: 2rem; }
        .hidden { display: none; }
        #mensaje { color: #b00020; font-weight: bold; }
      </style>
    </head>
    <body>
      <p id="mensaje"></p>

      <!-- Pantalla de Login -->
      <div id="loginView">
        <h2>Iniciar sesión</h2>
        <form id="loginForm">
          <input id="email" type="email" placeholder="Email" required />
          <input id="password" type="password" placeholder="Contraseña" required />
          <button type="submit">Entrar</button>
        </form>
      </div>

      <!-- Vista de Lista de Usuarios -->
      <div id="userListView" class="hidden">
        <h2>Usuarios</h2>
        <button id="btnLogout" type="button">Cerrar sesión</button>
        <ul id="lista"></ul>
      </div>

      <script>
        const loginView = document.getElementById("loginView");
        const userListView = document.getElementById("userListView");
        const loginForm = document.getElementById("loginForm");
        const btnLogout = document.getElementById("btnLogout");
        const listaEl = document.getElementById("lista");
        const mensajeEl = document.getElementById("mensaje");

        async function apiFetch(url, options = {}, onUnauthorized = null) {
          const token = localStorage.getItem("token");

          const headers = {
            ...(options.headers || {}),
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          };

          const res = await fetch(url, { ...options, headers });

          if (res.status === 401 && typeof onUnauthorized === "function") {
            onUnauthorized("Tu sesión venció");
            return null;
          }

          return res;
        }

        function cerrarSesion(motivo = "") {
          localStorage.removeItem("token");
          mensajeEl.textContent = motivo;
          userListView.classList.add("hidden");
          loginView.classList.remove("hidden");
        }

        function mostrarUsuarios() {
          mensajeEl.textContent = "";
          loginView.classList.add("hidden");
          userListView.classList.remove("hidden");
        }

        async function cargarUserList(onUnauthorized) {
          const res = await apiFetch("/user", {}, onUnauthorized);
          if (!res) return;

          if (res.ok) {
            const users = await res.json();
            listaEl.innerHTML = "";
            users.forEach((u) => {
              const li = document.createElement("li");
              li.textContent = u.name;
              listaEl.appendChild(li);
            });
            mostrarUsuarios();
          }
        }

        loginForm.addEventListener("submit", async (e) => {
          e.preventDefault();
          mensajeEl.textContent = "";

          const res = await fetch("/login", {
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
          await cargarUserList((msg) => cerrarSesion(msg));
        });

        btnLogout.addEventListener("click", () => cerrarSesion(""));

        if (localStorage.getItem("token")) {
          cargarUserList((msg) => cerrarSesion(msg));
        }
      </script>
    </body>
    </html>
    """