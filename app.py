import os
import json
import random
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="El Sorteo del Terror Navideño")

# Permitir leer archivos estáticos (como fotos) desde la carpeta actual AS
app.mount("/static", StaticFiles(directory="."), name="static")

DATA_FILE = "estado_sorteo.json"

# FECHA Y HORA DE DESBLOQUEO: 5 de Octubre de 2026 a las 4:00 PM (16:00 hs)
FECHA_DESBLOQUEO = datetime(2026, 10, 5, 16, 0, 0)

def cargar_estado():
    if not os.path.exists(DATA_FILE):
        participantes = [
            "LUZ MARINA", "RICARDO", "ALBEIRO", "VICTORIA", "BRUNO", 
            "LIA", "LUISA", "CARLOS", "DIVA", "PAULINA", 
            "ESPERANZA", "CONSUELO", "CILIO", "LUCIANA", "ANDRES", 
            "RUBY", "CAROLINA", "GUILLERMO", "JULIANA", "FELIPE", 
            "ANA", "CRISTIAN", "LAURA", "ALMA", "ZOE"
        ]
        data = {
            "participantes": participantes,
            "disponibles": participantes.copy(),
            "asignaciones": {},
            "gustos": {p: "" for p in participantes}
        }
        guardar_estado(data)
        return data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_estado(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class PeticionGustos(BaseModel):
    nombre: str
    gustos: str

class PeticionSorteo(BaseModel):
    nombre: str

# Redirigir la raíz al nuevo enlace personalizado
@app.get("/")
def raiz_redireccion():
    return RedirectResponse(url="/amigo-secreto-navideno-2026")

# Nueva ruta con el nombre personalizado
@app.get("/amigo-secreto-navideno-2026", response_class=HTMLResponse)
def leer_raiz():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Falta el archivo index.html en la carpeta AS</h1>"

@app.get("/api/estado")
def obtener_estado():
    data = cargar_estado()
    ahora = datetime.now()
    sorteo_habilitado = ahora >= FECHA_DESBLOQUEO
    
    return {
        "participantes": data["participantes"],
        "sorteo_habilitado": sorteo_habilitado,
        "fecha_desbloqueo": "5 de Noviembre de 2026 a las 4:00 PM"
    }

@app.get("/api/gustos/{nombre}")
def obtener_gustos_usuario(nombre: str):
    data = cargar_estado()
    gustos_actuales = data.get("gustos", {}).get(nombre, "")
    ya_guardado = bool(gustos_actuales.strip())
    return {
        "gustos": gustos_actuales,
        "ya_guardado": ya_guardado
    }

@app.post("/api/guardar-gustos")
def guardar_gustos(peticion: PeticionGustos):
    data = cargar_estado()
    nombre = peticion.nombre.strip()
    if nombre not in data["participantes"]:
        raise HTTPException(status_code=400, detail="Usuario no registrado.")
    
    if "gustos" not in data:
        data["gustos"] = {}
        
    gustos_existentes = data["gustos"].get(nombre, "").strip()
    if gustos_existentes:
        raise HTTPException(status_code=400, detail="¡Tú ya registraste tus gustos anteriormente y no se pueden modificar!")

    data["gustos"][nombre] = peticion.gustos.strip()
    guardar_estado(data)
    return {"mensaje": "Gustos guardados correctamente."}

@app.post("/api/sortear")
def realizar_sorteo(peticion: PeticionSorteo):
    ahora = datetime.now()
    if ahora < FECHA_DESBLOQUEO:
        raise HTTPException(status_code=400, detail="El sorteo aún no está habilitado. Se abrirá el 5 de noviembre a las 4:00 PM.")

    data = cargar_estado()
    usuario = peticion.nombre.strip()

    if usuario not in data["participantes"]:
        raise HTTPException(status_code=400, detail="Usuario no registrado.")

    if usuario in data["asignaciones"]:
        amigo = data["asignaciones"][usuario]
        gustos_amigo = data.get("gustos", {}).get(amigo, "No ha registrado sus gustos aún.")
        return {
            "repetido": True,
            "amigo_secreto": amigo,
            "gustos_amigo": gustos_amigo
        }

    opciones = [p for p in data["disponibles"] if p != usuario]

    if not opciones:
        raise HTTPException(status_code=400, detail="No hay opciones disponibles válidas.")

    elegido = random.choice(opciones)
    data["disponibles"].remove(elegido)
    data["asignaciones"][usuario] = elegido
    guardar_estado(data)

    gustos_amigo = data.get("gustos", {}).get(elegido, "No ha registrado sus gustos aún.")

    return {
        "repetido": False,
        "amigo_secreto": elegido,
        "gustos_amigo": gustos_amigo
    }
