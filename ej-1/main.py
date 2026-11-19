from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        3: {
        "id": 3,
        "name": "Roberto Gamarra",
        "email": "roberto@ejemplo.com",
        "edad": 42,
        "pais": "Argentino",
        "roles": ["user"],
    },
}


@app.get("/user")
def listar_usuarios():
    # Solo id y name en el listado
    return [{"id": u["id"], "name": u["name"]} for u in USUARIOS_DB.values()]


@app.get("/user/{user_id}")
def obtener_usuario(user_id: int):
    usuario = USUARIOS_DB.get(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario