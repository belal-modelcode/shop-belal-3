"""FastAPI application - E-commerce REST API."""

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from ecommerce.config import settings
from ecommerce.database import init_db
from ecommerce.users.api import router as users_router
from ecommerce.products.api import router as products_router
from ecommerce.products.api import categories_router
from ecommerce.orders.api import router as orders_router
from ecommerce.inventory.api import router as inventory_router
from ecommerce.reports.api import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title=settings.app_title,
    description="A RESTful e-commerce backend API",
    version="1.0.0",
    lifespan=lifespan,
)

# API v1 parent router
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(users_router)
api_v1_router.include_router(categories_router)
api_v1_router.include_router(products_router)
api_v1_router.include_router(orders_router)
api_v1_router.include_router(inventory_router)
api_v1_router.include_router(reports_router)

app.include_router(api_v1_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ecommerce-api"}
