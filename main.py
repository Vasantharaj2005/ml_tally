from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import invoice
from routers import tally  # <-- Import the new tally router
from routers import forecast # for forecast the sales
from routers import sales_prediction
from database import engine, Base


app = FastAPI()

# Create tables on startup
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Optional CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(invoice.router, prefix="/invoices", tags=["Invoices"])
app.include_router(tally.router, prefix="/tally", tags=["Tally"])  # New tally endpoint
app.include_router(forecast.router, prefix="/forecast",tags=["Forecast"])
app.include_router(sales_prediction.router,prefix="/sales-prediction",tags=["Sales Prediction"])

