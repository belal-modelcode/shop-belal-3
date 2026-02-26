"""FastAPI application - E-commerce monolith."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from ecommerce.database import init_db
from ecommerce.users.api import router as users_router
from ecommerce.products.api import router as products_router
from ecommerce.products.api import categories_router
from ecommerce.orders.api import router as orders_router
from ecommerce.inventory.api import router as inventory_router
from ecommerce.reports.api import router as reports_router
from ecommerce.reports.api import views_router as reports_views_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="E-commerce Monolith",
    description="A simple e-commerce backend demonstrating monolithic architecture",
    version="1.0.0",
    lifespan=lifespan,
)

# Register all routers
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(inventory_router)
app.include_router(reports_router)
app.include_router(reports_views_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ecommerce-monolith"}
