from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import asyncio
import time

from week2.app.database import get_db
from week2.app import crud
from week2.app.logger import logger

router = APIRouter(tags=["Counts"])


@router.get("/customers/count")
def customers_count(
    db: Session = Depends(get_db)
):
    logger.info("GET /customers/count")

    return {
        "customers":
        crud.get_customers_count(db)
    }


@router.get("/orders/count")
def orders_count(
    db: Session = Depends(get_db)
):
    return {
        "orders":
        crud.get_orders_count(db)
    }


@router.get("/products/count")
def products_count(
    db: Session = Depends(get_db)
):
    return {
        "products":
        crud.get_products_count(db)
    }


@router.get("/employees/count")
def employees_count(
    db: Session = Depends(get_db)
):
    return {
        "employees":
        crud.get_employees_count(db)
    }


@router.get("/offices/count")
def offices_count(
    db: Session = Depends(get_db)
):
    return {
        "offices":
        crud.get_offices_count(db)
    }


@router.get("/payments/count")
def payments_count(
    db: Session = Depends(get_db)
):
    return {
        "payments":
        crud.get_payments_count(db)
    }


@router.get("/orderdetails/count")
def orderdetails_count(
    db: Session = Depends(get_db)
):
    return {
        "orderdetails":
        crud.get_orderdetails_count(db)
    }


@router.get("/productlines/count")
def productlines_count(
    db: Session = Depends(get_db)
):
    return {
        "productlines":
        crud.get_productlines_count(db)
    }

async def async_customers_count(db):
    return crud.get_customers_count(db)


async def async_orders_count(db):
    return crud.get_orders_count(db)


async def async_products_count(db):
    return crud.get_products_count(db)


async def async_employees_count(db):
    return crud.get_employees_count(db)


async def async_offices_count(db):
    return crud.get_offices_count(db)


async def async_payments_count(db):
    return crud.get_payments_count(db)


async def async_orderdetails_count(db):
    return crud.get_orderdetails_count(db)


async def async_productlines_count(db):
    return crud.get_productlines_count(db)


@router.get("/overall_counts")
async def overall_counts(
    db: Session = Depends(get_db)
):
    logger.info(
        "Starting concurrent overall counts"
    )

    start_time = time.time()

    results = await asyncio.gather(
        async_customers_count(db),
        async_orders_count(db),
        async_products_count(db),
        async_employees_count(db),
        async_offices_count(db),
        async_payments_count(db),
        async_orderdetails_count(db),
        async_productlines_count(db)
    )

    end_time = time.time()

    logger.info(
        f"Completed in {end_time - start_time} seconds"
    )

    return {
        "customers": results[0],
        "orders": results[1],
        "products": results[2],
        "employees": results[3],
        "offices": results[4],
        "payments": results[5],
        "orderdetails": results[6],
        "productlines": results[7]
    }