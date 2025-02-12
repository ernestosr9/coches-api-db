import os
from sqlmodel import create_engine, SQLModel, Session
from src.models.coche import Coche

db_user: str = "quevedo"  
db_password: str =  "1234"
db_server: str = "fastapi-db" 
db_port: int = 3306  #SE PONE EL PUERTO DEFECTO DE DOCKER
db_name: str = "cochesdb"  

DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_server}:{db_port}/{db_name}"
engine = create_engine(os.getenv("db_url",DATABASE_URL), echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Coche(matricula="1234ABC", modelo="Seat Ibiza", km_totales=60000))
        session.add(Coche(matricula="3321GNN", modelo="Renault Scenic", km_totales=131400))
        session.add(Coche(matricula="9999AQR", modelo="Maserati", km_totales=4300))
        session.commit()
        #session.refresh_all()