from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class ItemIn(BaseModel):
    name: str
    description: str = ""


class Item(ItemIn):
    id: int


items_db: dict[int, Item] = {}
next_id = 1


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/items")
def list_items() -> list[Item]:
    return list(items_db.values())


@app.post("/items", response_model=Item)
def create_item(payload: ItemIn) -> Item:
    global next_id

    item = Item(id=next_id, **payload.model_dump())
    items_db[next_id] = item
    next_id += 1
    return item


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, payload: ItemIn) -> Item:
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    updated = Item(id=item_id, **payload.model_dump())
    items_db[item_id] = updated
    return updated


@app.delete("/items/{item_id}")
def delete_item(item_id: int) -> dict[str, str]:
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    del items_db[item_id]
    return {"message": "Item deleted"}
