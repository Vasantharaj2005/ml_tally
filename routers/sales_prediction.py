from fastapi import Depends, APIRouter
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from statistics.analytics import (get_invoice_date_amount_df,
                                  forecast)

router = APIRouter()


"""
This module contains routes for sales prediction using the Prophet library.
It includes routes to predict sales for the next day, week, and month."""

# Route the predict the sales for the next day
@router.get("/predict/day")
async def predict_day(session=Depends(get_db)):
    """
    Predict the sales for the next day.
    """
    df = await get_invoice_date_amount_df(session)
    return await forecast(df, 1)


# Route the predict the sales for the next week
@router.get("/predict/week")
async def predict_week(session=Depends(get_db)):
    """
    Predict the sales for the next week.
    """
    df = await get_invoice_date_amount_df(session)
    return await forecast(df, 7)


# Route the predict the sales for the next month
@router.get("/predict/month")
async def predict_month(session=Depends(get_db)):
    """
    Predict the sales for the next month."""
    df = await get_invoice_date_amount_df(session)
    return await forecast(df, 30)