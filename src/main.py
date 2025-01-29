from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select, func

from src.models.coche import Coche
from src.data.db import init_db, get_session


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    yield


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(lifespan=lifespan)


@app.get("/coches", response_model=list[Coche])
def lista_coches(session: SessionDep):
    coches = session.exec(select(Coche)).all()
    return coches


@app.get("/coches/media")
def media_km(session: SessionDep):
    coches = session.exec(select(Coche)).all()
    total_km = 0
    for coche in coches:
        total_km += coche.km_totales
    media = total_km / len(coches)
    return {"media_km": media}

@app.get("/coches/media-sql")
def media_km_sql(session: SessionDep):
    media = session.exec(select(func.avg(Coche.km_totales))).first()
    return {"media_km": media}

@app.get("/coches/mas-nuevo", response_model=Coche)
def mas_nuevo(session: SessionDep):
    coches = session.exec(select(Coche)).all()
    coche_mas_nuevo = None
    for coche in coches:
        if coche_mas_nuevo is None or coche_mas_nuevo.km_totales > coche.km_totales:
            coche_mas_nuevo = coche
    return coche_mas_nuevo

@app.get("/coches/mas-nuevo-sql", response_model=Coche)
def mas_nuevo_sql(session: SessionDep):
    coche_mas_nuevo = session.exec(select(Coche).order_by(Coche.km_totales.asc())).first()
    return coche_mas_nuevo

@app.get("/coches/{coche_matricula}", response_model=Coche)
def buscar_coche(coche_matricula: str, session: SessionDep):
    coche_encontrado = session.get(Coche, coche_matricula)
    if not coche_encontrado:
        raise HTTPException(status_code=404, detail="Coche no encontrado")
    return coche_encontrado

@app.post("/coches", response_model=Coche)
def nuevo_coche(coche: Coche, session: SessionDep):
    coche_encontrado = session.get(Coche, coche.matricula)
    if coche_encontrado:
        raise HTTPException(status_code=400, detail="Coche ya existe")
    session.add(coche)
    session.commit()
    session.refresh(coche)
    return coche

@app.delete("/coches/{coche_matricula}")
def borrar_serie(coche_matricula: str, session: SessionDep):
    coche_encontrado = session.get(Coche, coche_matricula)
    if not coche_encontrado:
        raise HTTPException(status_code=404, detail="Coche no encontrado")
    session.delete(coche_encontrado)
    session.commit()
    return {"mensaje": "Coche eliminado"}


@app.patch("/coches/{coche_matricula}", response_model=Coche)
def actualiza_coche(coche_matricula: str, coche: Coche, session: SessionDep):
    coche_encontrado = session.get(Coche, coche_matricula)
    if not coche_encontrado:
        raise HTTPException(status_code=404, detail="Coche no encontrado")
    coche_data = coche.model_dump(exclude_unset=True)
    coche_encontrado.sqlmodel_update(coche_data)
    session.add(coche_encontrado)
    session.commit()
    session.refresh(coche_encontrado)
    return coche_encontrado

@app.put("/coches", response_model=Coche)
def reemplaza_coche(coche: Coche, session: SessionDep):
    coche_encontrado = session.get(Coche, coche.matricula)
    if not coche_encontrado:
        raise HTTPException(status_code=404, detail="Coche no encontrado")
    coche_data = coche.model_dump()
    coche_encontrado.sqlmodel_update(coche_data)
    session.add(coche_encontrado)
    session.commit()
    session.refresh(coche_encontrado)
    return coche_encontrado
