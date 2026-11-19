from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()


class UserDetail(BaseModel):
    id: int
    name: str
    email: str
    edad: int
    pais: str
    roles: list[str]


USUARIOS_DB: dict[int, UserDetail] = {
    1: UserDetail(
        id=1,
        name="Martina",
        email="martina@ejemplo.com",
        edad=27,
        pais="Argentina",
        roles=["ADMIN"],
    ),
    2: UserDetail(
        id=2,
        name="Lucas",
        email="lucas@ejemplo.com",
        edad=31,
        pais="Uruguay",
        roles=["USER", "EDITOR"],
    ),
}


@app.get("/user")
def listar_usuarios():
    return [{"id": u.id, "name": u.name} for u in USUARIOS_DB.values()]


@app.get("/user/{user_id}", response_model=UserDetail)
def obtener_usuario(user_id: int):
    usuario = USUARIOS_DB.get(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@app.get("/", response_class=HTMLResponse)
def vista_roles():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <title>Práctica 4 - Mostrar mis roles</title>
      <style>
        body { font-family: sans-serif; padding: 2rem; }
        li { cursor: pointer; margin-bottom: 0.4rem; }
      </style>
    </head>
    <body>
      <h1 id="saludo">Hola, ...</h1>

      <h3>Usuarios</h3>
      <ul id="lista"></ul>

      <script>
        const saludoEl = document.getElementById("saludo");
        const listaEl = document.getElementById("lista");

        function formatearSaludo(user) {
          const rolesTexto = (user.roles || [])
            .map((rol) => rol.toUpperCase())
            .join(", ");
          return rolesTexto
            ? `Hola, ${user.name} (${rolesTexto})`
            : `Hola, ${user.name}`;
        }

        async function cargarUsuarioDetalle(id) {
          const res = await fetch(`/user/${id}`);
          const data = await res.json();
          if (res.ok) {
            saludoEl.textContent = formatearSaludo(data);
          }
        }

        async function init() {
          const res = await fetch("/user");
          const users = await res.json();

          users.forEach((u) => {
            const li = document.createElement("li");
            li.textContent = u.name;
            li.onclick = () => cargarUsuarioDetalle(u.id);
            listaEl.appendChild(li);
          });

          // Carga inicial del usuario 1 (Martina) para mostrar el saludo
          if (users.length > 0) {
            cargarUsuarioDetalle(users[0].id);
          }
        }

        init();
      </script>
    </body>
    </html>
    """