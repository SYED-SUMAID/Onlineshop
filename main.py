from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException , Depends
from sqlalchemy import event
from sqlmodel import Field, Session, SQLModel, create_engine, select

BASE = Path(__file__).resolve().parent
engine = create_engine(f"sqlite:///{BASE /'Shop.db'}", connect_args={"check_same_thread": False})

@event.listens_for(engine,"connect")
def fk_on(conn, _):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()

def get_session():
    with Session(engine) as s:
        yield s
    
class product(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = " "
    price_cents: int
    stock: int = 0
    emoji: str = "📦"

SQLModel.metadata.create_all(engine)

with Session(engine) as s:
    if not s.exec(select(product)).first():
           
        s.add_all([
            product(name="Product 1", description="Description 1", price_cents=1000, stock=10),
            product(name="Product 2", description="Description 2", price_cents=2000, stock=20),
            product(name="Product 3", description="Description 3", price_cents=3000, stock=30),
        ])
        s.commit()
app = FastAPI(title="Shop API")

@app.get("/products", response_model=List[product])
def get_products(session: Session = Depends(get_session)):
    products = session.exec(select(product)).all()
    return products
    
