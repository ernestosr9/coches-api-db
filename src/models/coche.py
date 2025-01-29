from sqlmodel import Field, SQLModel

class Coche(SQLModel, table=True):
    matricula: str | None = Field(default=None, primary_key=True)
    modelo: str = Field(index=True, max_length=50)
    km_totales: int = Field(gt=0)

