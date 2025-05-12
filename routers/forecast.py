from fastapi import Depends, APIRouter
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from statistics.analytics import (get_weekly_revenue,
                                  get_monthly_revenue,
                                  get_quarterly_revenue,
                                  top_sold_items,
                                  top_revenue_items)

router = APIRouter()

"""
This module contains routes for analytics related to sales and revenue.
It includes routes to get weekly, monthly, and quarterly revenue,
as well as the top sold items and top revenue items."""

#Routing for the weekly revenue
@router.get("/analytics/-weekly-revenue")
async def weekly_revenue(db: AsyncSession = Depends(get_db)):
    """
    Returns the weekly revenue.
    """
    return await get_weekly_revenue(db)

#Routing for the monthly revenue
@router.get("/analytics/monthly-revenue")
async def monthly_revenue(db: AsyncSession = Depends(get_db)):
    """
    Returns the monthly revenue.
    """
    return await get_monthly_revenue(db)

#Routing for the quarterly revenue
@router.get("/analytics/quarterly-revenue")
async def quarterly_revenue(db: AsyncSession = Depends(get_db)):
    """
    Returns the quarterly revenue."""
    return await get_quarterly_revenue(db)

#Routing for the top sold items
@router.get("/analytics/top-sold")
async def top_sold(session=Depends(get_db)):
    """
    Returns the top 5 sold items.
    """
    return await top_sold_items(session)

#Routing for the top revenue items
@router.get("/analytics/top-products")
async def top_products(session=Depends(get_db)):
    """
    Returns the top 5 products by revenue.
    """
    return await top_revenue_items(session)



