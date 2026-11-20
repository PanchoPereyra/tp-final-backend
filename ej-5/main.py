from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()

PAISES_DB = {
    1: "Argentina",
    2: "Brasil",
}


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0)
    email: str
    password: str = Field(..., min_length=4)
    country_id: int


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    age: int
    country_id: int
    country: str
    roles: list[str]


USUARIOS_DB: dict[int, UserOut] = {
    1: UserOut(
        id=1,
        name="Martina",
        email="martina@ejemplo.com",
        age=27,
        country_id=1,
        country="Argentina",
        roles=["ADMIN"],
    ),
}
next_user_id = 2


@app.get("/user")
def listar_usuarios():
    return [{"id": u.id, "name": u.name} for u in USUARIOS_DB.values()]


@app.get("/user/{user_id}", response_model=UserOut)
def obtener_usuario(user_id: int):
    usuario = USUARIOS_DB.get(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.post("/user", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(payload: UserCreate):
    global next_user_id

    if payload.country_id not in PAISES_DB:
        raise HTTPException(status_code=400, detail="País inválido")

    nuevo = UserOut(
        id=next_user_id,
        name=payload.name.strip(),
        email=payload.email,
        age=payload.age,
        country_id=payload.country_id,
        country=PAISES_DB[payload.country_id],
        roles=["USER"],
    )
    USUARIOS_DB[next_user_id] = nuevo
    next_user_id += 1
    return nuevo
@app.get("/", response_class=HTMLResponse)
def vista_alta_usuario():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <title>Práctica 5 - Alta de usuario</title>
      <style>
        body { font-family: sans-serif; display: flex; gap: 3rem; padding: 2rem; }
        form { display: flex; flex-direction: column; gap: 0.6rem; max-width: 280px; }
        li { cursor: pointer; margin-bottom: 0.4rem; }
      </style>
    </head>
    <body>
      <div>
        <h2>Alta de usuario</h2>
        <form id="formUsuario">
          <input id="name" type="text" placeholder="Nombre" required />
          <input id="age" type="number" placeholder="Edad" required />
          <input id="email" type="email" placeholder="Email" required />
          <input id="password" type="password" placeholder="Contraseña" minlength="4" required />
          <select id="country_id">
            <option value="1">Argentina</option>
            <option value="2">Brasil</option>
          </select>
          <button type="submit">Crear usuario</button>
        </form>
        <p id="mensajeApi"></p>
      </div>

      <div>
        <h2>Lista de usuarios</h2>
        <ul id="lista"></ul>
      </div>

      <script>
        const form = document.getElementById("formUsuario");
        const mensajeApi = document.getElementById("mensajeApi");
        const listaEl = document.getElementById("lista");

        function renderLista(users) {
          listaEl.innerHTML = "";
          users.forEach((u) => {
            const li = document.createElement("li");
            li.textContent = u.name;
            listaEl.appendChild(li);
          });
        }

        async function cargarLista() {
          const res = await fetch("/user");
          if (res.ok) {
            const users = await res.json();
            renderLista(users);
          }
        }

        form.addEventListener("submit", async (e) => {
          e.preventDefault();
          mensajeApi.textContent = "Enviando...";

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
            // Si FastAPI devuelve detail como string o lista de errores de validación
            const detailTexto = Array.isArray(data.detail)
              ? data.detail.map((d) => d.msg).join(", ")
              : (data.detail || JSON.stringify(data));
            mensajeApi.textContent = `Respuesta API: ${detailTexto}`;
            return;
          }

          mensajeApi.textContent = `Usuario creado: ${data.name} (ID ${data.id})`;
          form.reset();
          await cargarLista(); // Actualiza la lista sin recargar la página
        });

        cargarLista();
      </script>
    </body>
    </html>
    """