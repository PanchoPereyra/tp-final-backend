from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()


class Usuario(BaseModel):
    id: int
    name: str
    age: int


USUARIOS_DB: dict[int, Usuario] = {
    1: Usuario(id=1, name="Martina", age=27),
    2: Usuario(id=2, name="Lucas", age=31),
    3: Usuario(id=3, name="Sofía", age=16),
    4: Usuario(id=4, name="Martina", age=58),
    5: Usuario(id=5, name="Lucas", age=69),
    6: Usuario(id=6, name="Sofía", age=61),
}


@app.get("/user")
def listar_usuarios():
    return [{"id": u.id, "name": u.name} for u in USUARIOS_DB.values()]


@app.get("/user_mayores")
def listar_usuarios_mayores():
    return [
        {"id": u.id, "name": u.name}
        for u in USUARIOS_DB.values()
        if u.age >= 18
    ]


@app.get("/", response_class=HTMLResponse)
def vista_mayores():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <title>Práctica 6 - Solo mayores de edad</title>
      <style>
        body { font-family: sans-serif; padding: 2rem; }
        button { padding: 0.4rem 0.8rem; margin-bottom: 1rem; cursor: pointer; }
      </style>
    </head>
    <body>
      <h2>Usuarios</h2>
      <button id="btnFiltro" type="button">Mostrar: Solo mayores</button>
      <ul id="lista"></ul>

      <script>
        const btnFiltro = document.getElementById("btnFiltro");
        const listaEl = document.getElementById("lista");
        let soloMayores = false;

        function renderLista(users) {
          listaEl.innerHTML = "";
          users.forEach((u) => {
            const li = document.createElement("li");
            li.textContent = u.name;
            listaEl.appendChild(li);
          });
        }

        async function cargarUsuarios() {
          const endpoint = soloMayores ? "/user_mayores" : "/user";
          const res = await fetch(endpoint);
          if (res.ok) {
            const data = await res.json();
            renderLista(data);
          }
          btnFiltro.textContent = soloMayores
            ? "Mostrando: Solo mayores (ver Todos)"
            : "Mostrando: Todos (ver Solo mayores)";
        }

        btnFiltro.addEventListener("click", () => {
          soloMayores = !soloMayores;
          cargarUsuarios();
        });

        cargarUsuarios();
      </script>
    </body>
    </html>
    """