from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from typing import List
from database import async_session, MyItem

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


class MyItemCreate(BaseModel):
    text: str
    is_done: bool = False

class MyItemRead(BaseModel):
    id: int
    text: str
    is_done: bool

# Dependency to get the database session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


@app.post("/items", response_model=MyItemRead)
async def create_item(item: MyItemCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_item = MyItem(text=item.text, is_done=item.is_done)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


@app.get("/items", response_model=List[MyItemRead])
async def list_items(limit: int = 10, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(MyItem).limit(limit))
        items = result.scalars().all()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


@app.get("/items/{item_id}", response_model=MyItemRead)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(MyItem).where(MyItem.id == item_id))
        item = result.scalar_one_or_none()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
