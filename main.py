from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Services
from schemas import ServiceCreate, ServiceResponse

# Crear la tabla en Neon si todavía no existe
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Services API")


# ====================================
# GET: Consultar todos los servicios
# ====================================
@app.get("/services", response_model=list[ServiceResponse])
def get_services(db: Session = Depends(get_db)):
    services = db.query(Services).all()
    return services


# ====================================
# GET: Consultar un servicio
# ====================================
@app.get("/services/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    service = db.query(Services).filter(
        Services.id == service_id
    ).first()

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return service


# ====================================
# POST: Registrar un servicio
# ====================================
@app.post("/services", response_model=ServiceResponse, status_code=201)
def create_service(
    data: ServiceCreate,
    db: Session = Depends(get_db)
):
    # Validar que el servicio no esté registrado
    existing = db.query(Services).filter(
        Services.name == data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Service already registered"
        )

    service = Services(
        name=data.name,
        price=data.price,
        description=data.description
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    return service