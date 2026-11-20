from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI()

PAISES_DB = {
    1: "Argentina",
    2: "Brasil",
}


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0)
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=4)
    country_id: int


class Usuario(BaseModel):
    id: int
    name: str
    email: str
    age: int
    country_id: int
    country: str
    created_by_user: bool = False


USUARIOS_DB: dict[int, Usuario] = {
    1: Usuario(
        id=1,
        name="Martina",
        email="martina@ejemplo.com",
        age=27,
        country_id=1,
        country="Argentina",
        created_by_user=False,
    ),
    2: Usuario(
        id=2,
        name="Federico",
        email="federico@ejemplo.com",
        age=30,
        country_id=1,
        country="Argentina",
        created_by_user=False,
    ),
}
next_user_id = 3


@app.get("/user")
def listar_usuarios():
    return [
        {"id": u.id, "name": u.name, "created_by_user": u.created_by_user}
        for u in USUARIOS_DB.values()
    ]


@app.post("/user", status_code=status.HTTP_201_CREATED)
def crear_usuario(payload: UserCreate):
    global next_user_id

    if payload.country_id not in PAISES_DB:
        raise HTTPException(status_code=400, detail="País inválido")

    nuevo = Usuario(
        id=next_user_id,
        name=payload.name.strip(),
        email=payload.email.strip(),
        age=payload.age,
        country_id=payload.country_id,
        country=PAISES_DB[payload.country_id],
        created_by_user=True,
    )
    USUARIOS_DB[next_user_id] = nuevo
    next_user_id += 1
    return {
        "id": nuevo.id,
        "name": nuevo.name,
        "email": nuevo.email,
        "age": nuevo.age,
        "country_id": nuevo.country_id,
        "country": nuevo.country,
        "created_by_user": nuevo.created_by_user,
    }


@app.delete("/user/{user_id}", status_code=status.HTTP_200_OK)
def borrar_usuario(user_id: int):
    usuario = USUARIOS_DB.get(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.name.lower() == "sfer":
        raise HTTPException(
            status_code=403,
            detail="Missing permission: delete_users",
        )

    if not usuario.created_by_user:
        raise HTTPException(
            status_code=403,
            detail="Solo podés borrar usuarios creados por vos",
        )

    del USUARIOS_DB[user_id]
    return {"mensaje": "Usuario eliminado", "id": user_id}


@app.get("/", response_class=HTMLResponse)
def vista_borrar():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <title>Práctica 7 - Borrar un usuario</title>
      <style>
        body { font-family: sans-serif; display: flex; gap: 3rem; padding: 2rem; }
        form { display: flex; flex-direction: column; gap: 0.6rem; width: 260px; }
        li { margin-bottom: 0.5rem; display: flex; gap: 0.75rem; align-items: center; }
        button { cursor: pointer; }
        #mensaje { font-weight: bold; min-height: 1.2rem; }
      </style>
    </head>
    <body>
      <div>
        <h2>Crear usuario</h2>
        <form id="formUsuario">
          <input id="name" type="text" placeholder="Nombre" required />
          <input id="age" type="number" placeholder="Edad" required />
          <input id="email" type="email" placeholder="Email" required />
          <input id="password" type="password" placeholder="Contraseña (mín. 4)" minlength="4" required />
          <select id="country_id">
            <option value="1">Argentina</option>
            <option value="2">Brasil</option>
          </select>
          <button type="submit">Crear usuario</button>
        </form>
      </div>

      <div>
        <h2>Usuarios</h2>
        <p id="mensaje"></p>
        <ul id="lista"></ul>
      </div>

      <script>
        const form = document.getElementById("formUsuario");
        const listaEl = document.getElementById("lista");
        const mensajeEl = document.getElementById("mensaje");
        let usuarios = [];

        function renderLista() {
          listaEl.innerHTML = "";
          usuarios.forEach((u) => {
            const li = document.createElement("li");
            const span = document.createElement("span");
            span.textContent = u.created_by_user ? `${u.name} (creado por vos)` : u.name;

            const btnBorrar = document.createElement("button");
            btnBorrar.type = "button";
            btnBorrar.textContent = "Borrar";
            btnBorrar.onclick = () => borrarUsuario(u);

            li.appendChild(span);
            li.appendChild(btnBorrar);
            listaEl.appendChild(li);
          });
        }

        form.addEventListener("submit", async (e) => {
          e.preventDefault();
          mensajeEl.textContent = "";

          const body = {
            name: document.getElementById("name").value,
            age: Number(document.getElementById("age").value),
            email: document.getElementById("email").value,
            password: document.getElementById("password").value,
            country_id: Number(document.getElementById("country_id").value),
          };

          const res = await fetch("/user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          });
          const data = await res.json();

          if (!res.ok) {
            const detailTexto = Array.isArray(data.detail)
              ? data.detail.map((d) => d.msg).join(", ")
              : (data.detail || `Error ${res.status}`);
            mensajeEl.textContent = detailTexto;
            return;
          }

          usuarios.push({
            id: data.id,
            name: data.name,
            created_by_user: data.created_by_user,
          });
          renderLista();
          form.reset();
          mensajeEl.textContent = `Usuario creado: ${data.name}`;
        });

        async function borrarUsuario(user) {
          mensajeEl.textContent = "";
          const confirmado = window.confirm(`¿Seguro que querés borrar a ${user.name}?`);
          if (!confirmado) return;

          try {
            const res = await fetch(`/user/${user.id}`, {
              method: "DELETE",
            });
            const data = await res.json();

            if (!res.ok) {
              mensajeEl.textContent = data.detail || `Error ${res.status}`;
              return;
            }

            usuarios = usuarios.filter((item) => item.id !== user.id);
            renderLista();
            mensajeEl.textContent = `Se borró a ${user.name}.`;
          } catch (err) {
            mensajeEl.textContent = "Error de conexión al borrar usuario.";
          }
        }

        async function cargarInicial() {
          const res = await fetch("/user");
          if (res.ok) {
            usuarios = await res.json();
            renderLista();
          }
        }

        cargarInicial();
      </script>
    </body>
    </html>
    """