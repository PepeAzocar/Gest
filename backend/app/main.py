from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, categories, customers, inventory, products, sales, warehouses
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Gest API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.uploads_dir), name="uploads")

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(warehouses.router)
app.include_router(inventory.router)
app.include_router(customers.router)
app.include_router(sales.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
