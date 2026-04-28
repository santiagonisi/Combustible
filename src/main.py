from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.routes import monthly_invoices, reports, vehicles, views, vouchers
from src.core.config import settings
from src.db.database import Base, engine
from src.models import monthly_invoice, vehicle, voucher


app = FastAPI(title=settings.app_name, version=settings.app_version)
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

app.include_router(views.router)
app.include_router(vehicles.router)
app.include_router(vouchers.router)
app.include_router(reports.router)
app.include_router(monthly_invoices.router)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
