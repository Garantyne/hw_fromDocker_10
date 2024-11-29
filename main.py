from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import BaseModel
import uuid


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base = declarative_base()

class Ingredient(Base):
    __tablename__ = "ingredient"

    id = Column(String, primary_key=True)  # Позволяем NULL, но это рискованно!
    name = Column(String, nullable=False)  #  name и type не должны быть NULL
    type = Column(Integer, nullable=False)


# Создание таблиц
try:
    Base.metadata.create_all(bind=engine)
    print("Таблицы базы данных созданы успешно.")
except SQLAlchemyError as e:
    print(f"Ошибка создания таблиц базы данных: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

class IngredientModel(BaseModel):
    id: str
    name: str
    type: int

@app.get("/")
def read_root():
    html_content = "<h2>Hello METANIT.COM!</h2>"
    return HTMLResponse(content=html_content)

@app.get("/ingredients")
def get_ingredients():
    try:
        db = SessionLocal()
        ingredients = db.query(Ingredient).all()
        db.close()
        return {"ingredients": [{"id": ing.id, "name": ing.name, "type": ing.type} for ing in ingredients]}
    except SQLAlchemyError as e:
        return {"error": f"Ошибка базы данных: {e}"}


@app.post("/ingredients", response_model=IngredientModel, status_code=201)
async def create_ingredient(ingredient: IngredientModel, request: Request):
    try:
        db = SessionLocal()
        new_ingredient = Ingredient(**ingredient.dict()) # Используем dict() для создания экземпляра
        db.add(new_ingredient)
        db.commit()
        db.close()
        return ingredient # Возвращаем данные из запроса
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Ингредиент с таким ID уже существует: {e}") #Обработка уникальности ID
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")