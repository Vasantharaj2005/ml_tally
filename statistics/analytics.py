import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.invoice import Invoice
from prophet import Prophet

"""
This module contains functions to perform various analytics on invoices.
It includes functions to load invoices from the database, calculate revenue over different time periods,
and forecast future sales using the Prophet library.
"""
async def load_invoices_as_df(session: AsyncSession):
    """Load invoices from the database and convert to DataFrame."""
    result = await session.execute(select(Invoice))
    records = result.scalars().all()
    df = pd.DataFrame([r.__dict__ for r in records])
    if df.empty:
        return df
    df.drop(columns=["_sa_instance_state"], inplace=True)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    return df

async def get_monthly_revenue(session: AsyncSession):
    """Get monthly revenue from invoices."""
    df = await load_invoices_as_df(session)
    if df.empty:
        return {}
    df.set_index("invoice_date", inplace=True)
    monthly = df.resample("M")["amount"].sum()
    return monthly.to_dict()

async def get_quarterly_revenue(session: AsyncSession):
    """Get quarterly revenue from invoices."""
    df = await load_invoices_as_df(session)
    if df.empty:
        return {}
    df.set_index("invoice_date", inplace=True)
    quarterly = df.resample("Q")["amount"].sum()
    return quarterly.to_dict()

async def get_weekly_revenue(session: AsyncSession):
    """Get weekly revenue from invoices."""
    df = await load_invoices_as_df(session)
    if df.empty:
        return {}
    df.set_index("invoice_date",inplace=True)
    weekly = df.resample("W")["amount"].sum()
    return weekly.to_dict()


async def top_sold_items(session):
    """Get top 5 sold items from invoices."""
    df = await load_invoices_as_df(session)
    return df["description"].value_counts().head(5).to_dict()

async def top_revenue_items(session):
    """Get top 5 products by revenue from invoices."""
    df = await load_invoices_as_df(session)
    revenue = df.groupby("description")["amount"].sum().sort_values(ascending=False)
    return revenue.head(5).to_dict()

async def get_invoice_date_amount_df(session):
    """Get invoice date and amount as DataFrame."""
    result = await session.execute(select(Invoice))
    data = result.scalars().all()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame([inv.__dict__ for inv in data])
    df.drop(columns=["_sa_instance_state"], inplace=True)
    df = df[["invoice_date", "amount"]].rename(columns={"invoice_date": "ds", "amount": "y"})
    df["ds"] = pd.to_datetime(df["ds"])
    return df

async def forecast(df: pd.DataFrame, days: int):
    """Forecast sales using Prophet."""
    if df.empty:
        return {"error": "No data available"}
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    result = forecast[["ds", "yhat"]].tail(days)
    return result.to_dict(orient="records")




