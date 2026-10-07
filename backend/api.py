from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend import database as db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.inicializar()
    yield


app = FastAPI(title="Mesa de Soporte TI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TicketNuevo(BaseModel):
    solicitante_id: int
    titulo: str
    descripcion: str
    categoria_id: int
    prioridad_id: int


class CambioResponsable(BaseModel):
    responsable_id: int


class CambioEstado(BaseModel):
    nuevo_estado: str


def error_http(e: ValueError) -> HTTPException:
    codigo = 404 if "no encontrado" in str(e).lower() else 400
    return HTTPException(status_code=codigo, detail=str(e))


@app.get("/catalogos")
def get_catalogos():
    return db.catalogos()


@app.get("/transiciones")
def get_transiciones():
    return db.TRANSICIONES_VALIDAS


@app.get("/resumen")
def get_resumen():
    total, por_estado = db.resumen()
    return {"total": total, "por_estado": por_estado}


@app.get("/tickets")
def get_tickets():
    return db.listar_tickets()


@app.post("/tickets", status_code=201)
def post_ticket(body: TicketNuevo):
    try:
        ticket_id = db.crear_ticket(
            body.solicitante_id,
            body.titulo,
            body.descripcion,
            body.categoria_id,
            body.prioridad_id,
        )
    except ValueError as e:
        raise error_http(e)
    return {"id": ticket_id}


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    ticket = db.obtener_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado.")
    return ticket


@app.get("/tickets/{ticket_id}/historial")
def get_historial(ticket_id: int):
    return db.historial(ticket_id)


@app.patch("/tickets/{ticket_id}/responsable")
def patch_responsable(ticket_id: int, body: CambioResponsable):
    try:
        db.asignar_responsable(ticket_id, body.responsable_id)
    except ValueError as e:
        raise error_http(e)
    return db.obtener_ticket(ticket_id)


@app.patch("/tickets/{ticket_id}/estado")
def patch_estado(ticket_id: int, body: CambioEstado):
    try:
        db.cambiar_estado(ticket_id, body.nuevo_estado)
    except ValueError as e:
        raise error_http(e)
    return db.obtener_ticket(ticket_id)


@app.get("/solicitantes/{solicitante_id}/tickets")
def get_tickets_solicitante(solicitante_id: int):
    return db.tickets_de_solicitante(solicitante_id)