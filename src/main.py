from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.routes import reports, vehicles, views, vouchers
from src.core.config import settings
from src.db.database import Base, engine
from src.models import vehicle, voucher  # noqa: F401


app = FastAPI(title=settings.app_name, version=settings.app_version)
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

app.include_router(views.router)
app.include_router(vehicles.router)
app.include_router(vouchers.router)
app.include_router(reports.router)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
